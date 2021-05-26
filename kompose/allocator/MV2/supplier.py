import datetime
import hashlib
import os
import pulsar
import sys
from termcolor import cprint

import MV2.schema
from MV2.trader import Trader


class Supplier(Trader):

    def fulfillment(self, allocation_uuid, finish_event):
        """Receive and process Job"""

        self.hashed_outputs = {}
        self.msgnum = 0

        super(Supplier, self).fulfillment(allocation_uuid, finish_event)

        self.supplier_commit_producer = self.market_producer("supplier_commit", MV2.schema.SupplierCommitSchema)

        self.checklist_consumer = self.pulsar_client.subscribe(
            topic=f"persistent://{self.customer_uuid}/{self.cfg.market_uuid}/checklist_{allocation_uuid}",
            schema=pulsar.schema.AvroSchema(MV2.schema.Checklist),
            subscription_name=f"{self.cfg.user_uuid}-checklist_{allocation_uuid}",
            initial_position=pulsar.InitialPosition.Latest,
            consumer_type=pulsar.ConsumerType.Exclusive,
            message_listener=self.checklist)

        self.output_producer = self.market_producer("output", MV2.schema.OutputDataSchema)

        self.input_consumer = self.pulsar_client.subscribe(
            topic=f"persistent://{self.customer_uuid}/{self.cfg.market_uuid}/input_{allocation_uuid}",
            schema=pulsar.schema.AvroSchema(MV2.schema.InputDataSchema),
            subscription_name=f"{self.cfg.user_uuid}-input_{allocation_uuid}",
            initial_position=pulsar.InitialPosition.Latest,
            consumer_type=pulsar.ConsumerType.Exclusive,
            message_listener=self.process)

        app_consumer = self.pulsar_client.subscribe(
            topic=f"persistent://{self.customer_uuid}/{self.cfg.market_uuid}/app_{allocation_uuid}",
            schema=pulsar.schema.AvroSchema(MV2.schema.AppSchema),
            subscription_name=f"{self.cfg.user_uuid}-app_{allocation_uuid}",
            initial_position=pulsar.InitialPosition.Latest,
            consumer_type=pulsar.ConsumerType.Exclusive,
            message_listener=self.setup)

        print(f"\napp_consumer.topic: {app_consumer.topic()}; pid:{os.getpid()}\n")

        print("Supplier is Waiting")
        self.finish_event.wait()
        print("Supplier is done Waiting")

    def process(self, consumer, msg):
        # TODO: send data to docker app for processing
        consumer.acknowledge_cumulative(msg)
        self.num_inputs = self.num_inputs + 1
        cprint(f"\n{self.cfg.user_uuid} recieve message:{self.num_inputs}; input value: {msg.value()}\n", "magenta")


        customertimestamp = msg.value().timestamp
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        input = msg.value().value
        output = input

        hash1_output = hashlib.sha256(str(output).encode("utf-8")).hexdigest()

        self.hashed_outputs[hash1_output] = {"output": output,
                                             "input_MessageId": msg.message_id().serialize()}


        output_msg = MV2.schema.OutputDataSchema(
            value=output,
            customertimestamp=customertimestamp,
            suppliertimestamp=now.timestamp(),
            input_uuid=msg.value().input_uuid,
            timestamp=now.timestamp()
        )


        self.output_producer.send(output_msg)

        sys.stdout.flush()

    # def cleanup(self, consumer, msg):
    #     consumer.acknowledge_cumulative(msg)
    #     self.pulsar_client.close()
    #     self.finish_event.set()


    def setup(self, consumer, msg):
        # TODO: fetch app, start docker

        consumer.acknowledge_cumulative(msg)
        cprint(f"\nuser: {self.cfg.user_uuid}; fetch app: {msg.value()}\n", "magenta")


    def cleanup(self, consumer, msg):
        pass

    def checklist(self, consumer, msg):
        consumer.acknowledge_cumulative(msg)
        allocation_uuid = msg.value().allocation_uuid
        user_uuid = self.cfg.user_uuid

        cprint(f"{self.cfg.user_uuid} receive checklist", "magenta")

        output_checklist = []
        input_MessageId_list = []
        for hashed_output in msg.value().checklist:
            if hashed_output in self.hashed_outputs:
                output_checklist.append(self.hashed_outputs[hashed_output]["output"])
                input_MessageId_list.append(self.hashed_outputs[hashed_output]["input_MessageId"])

        hashed_output_checklist = hashlib.sha256(str(output_checklist).encode("utf-8")).hexdigest()

        cprint(f"\n{self.cfg.user_uuid}; "
               f"\nhashed_outputs:{self.hashed_outputs}"
               f"\noutput_checklist:{output_checklist}; "
               f"\n hash1: {hashed_output_checklist};"
               f"\ninput_MessageId_list: {input_MessageId_list}", "magenta")

        self.ledger_client.postOutput(allocation_uuid, user_uuid, hashed_output_checklist, input_MessageId_list)



        # TODO: post output to ledger
        self.ledger_client.postOutput()

    def sign(self, allocation_uuid):
        cprint(f"{self.cfg.user_uuid} Signing", "magenta")
        # TODO: Commit to ledger
        # TODO: Sign on ledger
        self.ledger_client.supplierSign(allocation_uuid, self.cfg.user_uuid)








