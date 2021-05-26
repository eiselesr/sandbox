import datetime
import hashlib
import sys

import pulsar
from termcolor import cprint
import time

import MV2.helpers.ledger
import MV2.schema


class Mediator:
    def __init__(self, cfg, finish_event):

        self.cfg = cfg
        self.finish_event = finish_event
        self.pulsar_client = pulsar.Client(cfg.pulsar_url)
        self.ledger_client = MV2.helpers.ledger.Client(cfg)

        self.offers = {}

        # producer - offers
        self.offer_producer = self.pulsar_client.create_producer(
            topic=f"persistent://{cfg.tenant}/{cfg.market_uuid}/{cfg.topic}",
            schema=pulsar.schema.AvroSchema(MV2.schema.ResourceSchema))

        self.market_consumer = self.pulsar_client.subscribe(
            topic=f"persistent://{cfg.tenant}/{cfg.market_uuid}/market",
            schema=pulsar.schema.AvroSchema(MV2.schema.MarketSchema),
            subscription_name=f"{cfg.user_uuid}-market-subscription",
            initial_position=pulsar.InitialPosition.Latest,
            consumer_type=pulsar.ConsumerType.Exclusive,
            message_listener=self.handle_ledger)


    def post_offer(self, offer):
        # print(f"type: {type(offer)}; post_offer: {offer.offer_uuid}")
        self.offers[f"{offer.user_uuid}_{offer.offer_uuid}"] = offer
        self.offer_producer.send(offer)

    def MediationRequested(self, msg):
        cprint(f"{self.cfg.user_uuid}; Mediation Request Received", "cyan")

        allocation_uuid = msg.value().allocation_uuid
        customer_uuid = msg.value().customer_uuid
        customer_hash = msg.value().customer_hash
        input_MessageId_list = msg.value().args_bytes

        cprint(f"msg.value(): {msg.value()}"
               f"input_MessageId_list: {input_MessageId_list}"
               f"\ncustomer_uuid: {customer_uuid}", "cyan")

        inputs = []
        for serial_msg_id in input_MessageId_list:
            msg_id = pulsar.MessageId.deserialize(serial_msg_id)
            reader = self.pulsar_client.create_reader(
                topic=f"persistent://{customer_uuid}/{self.cfg.market_uuid}/input_{allocation_uuid}",
                start_message_id=msg_id,
                schema=pulsar.schema.AvroSchema(MV2.schema.InputDataSchema)
            )

            msg = reader.read_next()
            time.sleep(.2)
            cprint(f"msg.value(): {msg.value()}", "cyan")
            input = msg.value().value
            inputs.append(input)

        self.setup()
        hashed_mediator_output = self.fulfillment(inputs)

        cprint(f"{self.cfg.user_uuid}: "
               f"\n mediator: {hashed_mediator_output}"
               f"\n hashed_customer_commit: {customer_hash}", "cyan")

        self.ledger_client.postMediation(allocation_uuid, hashed_mediator_output)
        sys.stdout.flush()




    def handle_ledger(self, consumer, msg):
        consumer.acknowledge_cumulative(msg)
        event = msg.value().event
        user_uuid = msg.value().user_uuid
        if event == "MediationRequested":
            getattr(self, event)(msg)


    # def process_verification(self, consumer, msg):
    #     # TODO: send data to app for processing
    #     consumer.acknowledge_cumulative(msg)
    #     print(f"\nProcess input: {msg.value()}\n")
    #
    #     if msg.value().result == "Match":
    #         print(f"user_uuid: {self.cfg.user_uuid}; Result: {msg.value().result}")
    #     else:
    #         customertimestamp = msg.value().timestamp
    #         now = datetime.datetime.now(tz=datetime.timezone.utc)
    #
    #         #TODO: Re-run relevant inputs and Compare results against hashes
    #         result = "Match"
    #         customer = ""
    #
    #         #TODO: fill out
    #         output = MV2.schema.MediationSchema(
    #             result=result,
    #             customer = customer,
    #             supplierspass = [],
    #             suppliersfail = [],
    #             allocation_uuid = msg.value().allocation_uuid,
    #             checktimestamp = msg.value().timestamp,
    #             mediationtimestamp = now.timestamp()
    #         )
    #
    #     # Send outcome of mediation
    #     self.mediation_producer.send(output)
    #     #TODO: write outcome to ledger
    #     self.ledger_client.PostMediation()

    # def cleanup(self, consumer, msg):
    #     consumer.acknowledge_cumulative(msg)
    #     self.pulsar_client.close()
    #     self.finish_event.set()


    def setup(self):
        # TODO: fetch app, start docker
        return 0

    def fulfillment(self, inputs):

        output_checklist = []
        for input in inputs:
            output = input
            output_checklist.append(output)

        hash1 = hashlib.sha256(str(output_checklist).encode("utf-8")).hexdigest()
        hashed_output_checklist = hashlib.sha256(hash1.encode("utf-8")).hexdigest()

        return hashed_output_checklist


    def sign(self, allocation_uuid):
        # TODO: Commit to ledger
        # TODO: Sign on ledger
        self.ledger_client.mediatorSign(allocation_uuid, self.cfg.user_uuid)






