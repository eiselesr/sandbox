import datetime
import os
import multiprocessing
import pulsar
import sys
from termcolor import cprint
import MV2.helpers.ledger
import MV2.helpers.PulsarREST as PulsarREST
import MV2.schema


class Trader:
    def __init__(self, cfg, schema):
        """set up allocation channel"""

        self.pulsar_client = pulsar.Client(cfg.pulsar_url)
        self.ledger_client = MV2.helpers.ledger.Client(cfg)


        # producer - offers
        self.offer_producer = self.pulsar_client.create_producer(
            topic=f"persistent://{cfg.tenant}/{cfg.market_uuid}/{cfg.topic}",
            schema=pulsar.schema.AvroSchema(schema))

        # producer - accept
        self.accept_producer = self.pulsar_client.create_producer(
            topic=f"persistent://{cfg.tenant}/{cfg.market_uuid}/accept",
            schema=pulsar.schema.AvroSchema(MV2.schema.AcceptSchema))

        # # consumer - allocations
        self.allocation_consumer = self.pulsar_client.subscribe(
            topic=f"persistent://{cfg.tenant}/{cfg.market_uuid}/allocations",
            schema=pulsar.schema.AvroSchema(MV2.schema.AllocationSchema),
            subscription_name=f"{cfg.user_uuid}-allocation-subscription",
            initial_position=pulsar.InitialPosition.Latest,
            consumer_type=pulsar.ConsumerType.Exclusive,
            message_listener=self.eval_allocation)

        self.cfg = cfg
        self.offers = {}
        self.allocations = {}
        self.processes = {}


        # consumer - accept
        self.accept_consumer = self.pulsar_client.subscribe(
            topic=f"persistent://{cfg.tenant}/{cfg.market_uuid}/accept",
            schema=pulsar.schema.AvroSchema(MV2.schema.AcceptSchema),
            subscription_name=f"{cfg.user_uuid}-accept-subscription",
            initial_position=pulsar.InitialPosition.Latest,
            consumer_type=pulsar.ConsumerType.Exclusive,
            message_listener=self.start_fulfillment)

        # consumer - accept
        self.market_consumer = self.pulsar_client.subscribe(
            topic=f"persistent://{cfg.tenant}/{cfg.market_uuid}/market",
            schema=pulsar.schema.AvroSchema(MV2.schema.MarketSchema),
            subscription_name=f"{cfg.user_uuid}-market-subscription",
            initial_position=pulsar.InitialPosition.Latest,
            consumer_type=pulsar.ConsumerType.Exclusive,
            message_listener=self.handle_ledger)

    def timeout(self):
        pass

    def ack_received(self, res, msg_id):
        print('uuid: %s; ACK RECEIVED: %s; msg_id: %s\n' %(self.cfg.user_uuid, res, msg_id))

    def post_offer(self, offer):
        # print(f"type: {type(offer)}; post_offer: {offer.offer_uuid}")
        self.offers[f"{offer.user_uuid}_{offer.offer_uuid}"] = offer
        self.offer_producer.send_async(offer, callback=self.ack_received)

        # self.offer_producer.send(offer, properties={"content-type": "application/json"})

    def eval_allocation(self, consumer, msg):
        print(f"{self.cfg.user_uuid} eval_allocation")
        self.cfg.print_msg(consumer, msg)
        ack = consumer.acknowledge(msg)

        status = False


        allocation_msg = msg.value()
        allocation_uuid = msg.value().allocation_uuid

        my_offers = [o for o in allocation_msg.allocation if o in self.offers]

        if my_offers:

            #TODO evaluate allcoation
            status = True


        if status:
            self.allocations[allocation_uuid] = {}
            self.allocations[allocation_uuid]["alloc_msg"] = allocation_msg
            self.allocations[allocation_uuid]["pending"] = allocation_msg.allocation
            self.allocations[allocation_uuid]["accepted"] = []
            print(f"{self.cfg.user_uuid} ALLOCATIONS: \n {self.allocations}"
                  f"\nAccepts Pending: {self.allocations[allocation_uuid]['pending']}")

            status = MV2.schema.AcceptSchema(
                allocation_uuid=allocation_uuid,
                offer_uuids=my_offers,
                status=status,
                timestamp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
            )

            if my_offers:
                for o in my_offers:
                    self.offers.pop(o, None)
            # if my_coffer:
            #     self.offers.pop(my_coffer, None)
            # if my_soffers:
            #     for so in my_soffers:
            #         self.offers.pop(so, None)


            self.accept_producer.send(status)


    def handle_ledger(self, consumer, msg):
        consumer.acknowledge_cumulative(msg)

        if msg.value().user_uuid == self.cfg.user_uuid:

            if msg.value().event == "AllocationCreated" or msg.value().event == "SupplierAdded":
                allocation_uuid = msg.value().allocation_uuid
                self.sign(allocation_uuid)


    def sign(self, allocation_uuid):
        pass

    def start_fulfillment(self, consumer, msg):
        """Fulfill job"""
        consumer.acknowledge_cumulative(msg)
        status = msg.value().status
        allocation_uuid = msg.value().allocation_uuid


        # Wait until all allocated agents accept
        for o in msg.value().offer_uuids:
            if o in self.allocations[allocation_uuid]["pending"]:
                if status == True:
                    offer_uuid = self.allocations[allocation_uuid]["pending"].remove(o)
                    self.allocations[allocation_uuid]["accepted"].append(o)

                    if not self.allocations[allocation_uuid]["pending"]:
                        finish_event = multiprocessing.Event()
                        self.processes[allocation_uuid] = {"p": multiprocessing.Process(target=self.fulfillment,
                                                                                      args=(allocation_uuid, finish_event)),
                                                           "e": finish_event}
                        print(f"\n{self.cfg.user_uuid}_{allocation_uuid} accepted: {status}\n")
                        self.processes[allocation_uuid]["p"].start()



    def fulfillment(self, allocation_uuid, finish_event):

        self.customer_uuid = self.allocations[allocation_uuid]["alloc_msg"].customer_uuid
        self.allocation_uuid = allocation_uuid

        while True:
            sys.stdout.flush()
            tenants = PulsarREST.get_tenants(pulsar_admin_url=self.cfg.pulsar_admin_url)
            if self.customer_uuid in tenants:
                break
            else:
                print(f"{self.cfg.user_uuid}, before doing anything, sleep to make sure tenant exists")
                time.sleep(1)
                continue

        while True:
            sys.stdout.flush()
            namespaces = PulsarREST.get_namespaces(pulsar_admin_url=self.cfg.pulsar_admin_url,
                                                   tenant=self.customer_uuid)
            if not namespaces:
                time.sleep(1)
                continue

            print(f"{self.customer_uuid}/{self.cfg.market_uuid} in namespaces: "
                  f"{self.customer_uuid}/{self.cfg.market_uuid}" in namespaces)

            if f"{self.customer_uuid}/{self.cfg.market_uuid}" not in namespaces:
                print(f"{self.cfg.user_uuid}, before doing anything, sleep to make sure namespace exists")
                time.sleep(1)
                continue
            else:
                break

        self.finish_event = finish_event
        self.pulsar_client = pulsar.Client(self.cfg.pulsar_url)
        self.num_inputs = 0

        print(f"\nSTART {self.cfg.user_uuid} fulfillment: {allocation_uuid}; "
              f"pid:{os.getpid()}; "
              f"Topic: {self.customer_uuid}/{self.cfg.market_uuid}/app_{allocation_uuid} \n")

        self.cleanup_consumer = self.pulsar_client.subscribe(
            topic=f"persistent://{self.customer_uuid}/{self.cfg.market_uuid}/cleanup_{allocation_uuid}",
            schema=pulsar.schema.AvroSchema(MV2.schema.CleanupDataSchema),
            subscription_name=f"{self.cfg.user_uuid}-cleanup_{allocation_uuid}",
            initial_position=pulsar.InitialPosition.Latest,
            consumer_type=pulsar.ConsumerType.Exclusive,
            message_listener=self.cleanup)


    def run(self):
        pass

    def stop(self):

        for allocation_uuid in self.processes:
            self.processes[allocation_uuid]["e"].set()
            self.processes[allocation_uuid]["p"].terminate()

        self.pulsar_client.close()

    def cleanup(self, consumer, msg):
        print(f"\nclose user_uuid: {self.cfg.user_uuid}; pid: {os.getpid()}\n")
        consumer.acknowledge_cumulative(msg)
        self.finish_event.set()
        # self.pulsar_client.close()

    def market_producer(self, topic, schema):
        producer = self.pulsar_client.create_producer(
            topic=f"persistent://{self.customer_uuid}/{self.cfg.market_uuid}/{topic}_{self.allocation_uuid}",
            schema=pulsar.schema.AvroSchema(schema)
        )
        return producer
