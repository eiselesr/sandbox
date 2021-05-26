import datetime
import multiprocessing
import pulsar
import sys
from termcolor import cprint
import time
import MV2.schema
import MV2.helpers.ledger


class Allocator:
    def __init__(self,cfg):

        self.ai = 0

        self.sq = multiprocessing.Queue()
        self.cq = multiprocessing.Queue()
        self.mq = multiprocessing.Queue()

        self.supplier_offers = {}
        self.customer_offers = {}
        self.mediator_offers = {}
        self.allocations = {}

        self.cfg = cfg

        self.pulsar_client = pulsar.Client(cfg.pulsar_url)


        # consumer - customer offers
        self.coffer_consumer = self.pulsar_client.subscribe(topic=f"persistent://{cfg.tenant}/{cfg.market_uuid}/customer_offers",
                                                            schema=pulsar.schema.AvroSchema(MV2.schema.ServiceSchema),
                                                            subscription_name=f"{cfg.user_uuid}-offer-subscription",
                                                            initial_position=pulsar.InitialPosition.Latest,
                                                            consumer_type=pulsar.ConsumerType.Exclusive,
                                                            message_listener=self.process_customer_offer)

        # consumer - supplier offers
        self.soffer_consumer = self.pulsar_client.subscribe(topic=f"persistent://{cfg.tenant}/{cfg.market_uuid}/supplier_offers",
                                                            schema=pulsar.schema.AvroSchema(MV2.schema.ResourceSchema),
                                                            subscription_name=f"{cfg.user_uuid}-offer-subscription",
                                                            initial_position=pulsar.InitialPosition.Latest,
                                                            consumer_type=pulsar.ConsumerType.Exclusive,
                                                            message_listener=self.process_supplier_offer
                                                            )

        # consumer - mediator offers
        self.moffer_consumer = self.pulsar_client.subscribe(
            topic=f"persistent://{cfg.tenant}/{cfg.market_uuid}/mediator_offers",
            schema=pulsar.schema.AvroSchema(MV2.schema.ResourceSchema),
            subscription_name=f"{cfg.user_uuid}-offer-subscription",
            initial_position=pulsar.InitialPosition.Latest,
            consumer_type=pulsar.ConsumerType.Exclusive,
            message_listener=self.process_mediator_offer
            )

        self.allocation_process = multiprocessing.Process(target=self.allocate, args=(self.sq, self.cq, self.mq))
        self.allocation_process.start()


    def process_customer_offer(self, consumer, msg):
        # print("\nprocess_customer_offer\n")
        consumer.acknowledge_cumulative(msg)
        # TODO: Check that offer is valid (i.e. that mediator is valid.)
        #  For now assume mediator is a reliable cloud service that is
        #  always available with fixed price so check is unnecessary
        self.cq.put(msg.value())

        # key = f"{msg.value().user_uuid}_{msg.value().offer_uuid}"
        # self.customer_offers[key] = msg.value()
        # self.allocate()


    def process_supplier_offer(self, consumer, msg):
        # print("\nprocess_supplier_offer\n")
        consumer.acknowledge_cumulative(msg)
        # TODO: Check that offer is valid
        self.sq.put(msg.value())

        # key = f"{msg.value().user_uuid}_{msg.value().offer_uuid}"
        # self.supplier_offers[key] = msg.value()
        # self.allocate()

    def process_mediator_offer(self, consumer, msg):
        consumer.acknowledge_cumulative(msg)
        # TODO: Check that offer is valid
        self.mq.put(msg.value())


    def allocate(self,sq, cq, mq):

        print("\nallocate loop started")

        self.ledger_client = MV2.helpers.ledger.Client(self.cfg)
        self.pulsar_client = pulsar.Client(self.cfg.pulsar_url)

        # producer - offers
        self.allocation_producer = self.pulsar_client.create_producer(
            topic=f"persistent://{self.cfg.tenant}/{self.cfg.market_uuid}/allocations",
            schema=pulsar.schema.AvroSchema(MV2.schema.AllocationSchema))

        # consumer - accept
        self.accept_consumer = self.pulsar_client.subscribe(
            topic=f"persistent://{self.cfg.tenant}/{self.cfg.market_uuid}/accept",
            schema=pulsar.schema.AvroSchema(MV2.schema.AcceptSchema),
            subscription_name=f"{self.cfg.user_uuid}-accept-subscription",
            initial_position=pulsar.InitialPosition.Latest,
            consumer_type=pulsar.ConsumerType.Exclusive,
            message_listener=self.start_fulfillment)

        # self.ledger_producer = self.pulsar_client.create_producer(
        #     topic=f"persistent://{self.cfg.tenant}/{self.cfg.market_uuid}/ledger",
        #     schema=pulsar.schema.AvroSchema(MV2.schema.LedgerSchema))

        print("allocation_producer created")

        first = True

        while True:

            sys.stdout.flush()

            if first:
                first = False
                print("Start allocate while loop\n")

            while not sq.empty():
                print("add supplier messages to sq")
                msgvalue = sq.get()
                key = f"{msgvalue.user_uuid}_{msgvalue.offer_uuid}"
                self.supplier_offers[key] = msgvalue
                # self.cfg.print_msgvalue(msgvalue)
                print(f"len: {len(self.supplier_offers)}; supplier offers: {self.supplier_offers}")

            while not cq.empty():
                print("add customer messages to cq")
                msgvalue = cq.get()
                key = f"{msgvalue.user_uuid}_{msgvalue.offer_uuid}"
                self.customer_offers[key] = msgvalue
                # self.cfg.print_msgvalue(msgvalue)
                print(f"len: {len(self.customer_offers)}; customer_offers: {self.customer_offers}")

            while not mq.empty():
                print("add mediator messages to mq")
                msgvalue = mq.get()
                key = f"{msgvalue.user_uuid}_{msgvalue.offer_uuid}"
                self.mediator_offers[key] = msgvalue
                # self.cfg.print_msgvalue(msgvalue)
                print(f"len: {len(self.mediator_offers)}; customer_offers: {self.mediator_offers}")

            if len(self.supplier_offers) > 0 and len(self.customer_offers) > 0 and len(self.mediator_offers):

                print("\nNEW Allocation")

                ckey = list(self.customer_offers)[0]
                skey = list(self.supplier_offers)[0]
                mkey = list(self.mediator_offers)[0]

                print(f"len: {len(self.supplier_offers)}; supplier offers: {self.supplier_offers}")
                print(f"len: {len(self.customer_offers)}; customer_offers: {self.customer_offers}")
                print(f"len: {len(self.mediator_offers)}; mediator_offers: {self.mediator_offers}")

                # TODO: allocation algorithm
                coffer = self.customer_offers.pop(ckey)
                soffer = self.supplier_offers.pop(skey)
                moffer = self.mediator_offers.pop(mkey)

                print(f"len: {len(self.supplier_offers)}; supplier offers: {self.supplier_offers}")
                print(f"len: {len(self.customer_offers)}; customer_offers: {self.customer_offers}")
                print(f"len: {len(self.mediator_offers)}; mediator_offers: {self.mediator_offers}")

                #
                # if coffer.replicas < len(self.supplier_offers):
                #     for i in range(coffer.replicas):
                #         key = supplier_offers.keys()
                #         soffer_ids.append(supplier_offers.pop(key))
                #
                #
                # allocation_uuid = str(uuid.uuid4())
                allocation_uuid = f"allocation_{self.ai}"
                print(f"allocation_uuid: {allocation_uuid}")

                self.ai = self.ai + 1
                # TODO: Compute a legitimate price
                price = round((coffer.end-coffer.start) * coffer.rate * coffer.cpu * coffer.price)*1.0
                cprint(f"\n{self.cfg.user_uuid} allocate duration: {coffer.end-coffer.start}", "yellow")
                cprint(f"\n{self.cfg.user_uuid} allocate price: {price}", "yellow")
                timestamp = datetime.datetime.now(tz=datetime.timezone.utc)
                allocation_msg = MV2.schema.AllocationSchema(
                    customer_uuid=coffer.user_uuid,  # include because this will be the tenant
                    allocation_uuid=allocation_uuid,
                    mediator_uuid=moffer.user_uuid,
                    supplier_uuids=[soffer.user_uuid],
                    allocation=[f"{coffer.user_uuid}_{coffer.offer_uuid}",
                                f"{soffer.user_uuid}_{soffer.offer_uuid}"],
                    # coffer_id=f"{coffer.user_uuid}_{coffer.offer_uuid}",
                    # soffer_ids=[soffer.offer_uuid],
                    start=coffer.start,
                    end=coffer.end,
                    price=price,
                    replicas=coffer.replicas,
                    timestamp=timestamp.timestamp()
                )

                # List to make sure all allocated agents accept
                self.allocations[allocation_uuid] = {}
                self.allocations[allocation_uuid]["msg"] = allocation_msg
                self.allocations[allocation_uuid]["pending"] = allocation_msg.allocation
                self.allocations[allocation_uuid]["accepted"] = []

                cprint(f"BLOCK UNTIL ACKED: {allocation_uuid}", "yellow")
                self.allocation_producer.send(allocation_msg)
                # self.allocation_producer.send_async(allocation, callback=self.ack_received)
                cprint(f"DONE BLOCKING: {allocation_uuid} \n", "yellow")

            else:
                time.sleep(1)
                cprint("no messages", "yellow")

    def ack_received(self, res, msg_id):
        print('uuid: %s; ALLOC ACK RECEIVED: %s; msg_id: %s\n' %(self.cfg.user_uuid, res, msg_id))

    def stop(self):
        self.pulsar_client.close()
        self.allocation_process.terminate()


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

                    # If all agents accept then create the allocation on the smart contract
                    if not self.allocations[allocation_uuid]["pending"]:
                        cprint(f"All allocated agents have accepted. Create Allocation on ledger ", "yellow")
                        alloc_msg = self.allocations[allocation_uuid]["msg"]
                        # TODO: pass arguments for message to the ledger.
                        cprint(f"\n{self.cfg.user_uuid} customer: {alloc_msg.customer_uuid}", "yellow")
                        self.ledger_client.createAllocation(
                            allocation_uuid,
                            alloc_msg)
                            # alloc_msg.customer_uuid,
                            # alloc_msg.mediator_uuid,
                            # alloc_msg.price)


                        cprint(f"\n{self.cfg.user_uuid} suppliers: {alloc_msg.supplier_uuids}", "yellow")
                        for supplier in alloc_msg.supplier_uuids:
                            self.ledger_client.addSupplier(allocation_uuid, supplier)


if __name__ == "__main__":

    alloc = Allocator()
