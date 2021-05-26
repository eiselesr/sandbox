import datetime
import hashlib
import os
import pulsar
import sys
from termcolor import cprint
import time
import uuid

import MV2.helpers.PulsarREST as PulsarREST
import MV2.schema
from MV2.trader import Trader

class Customer(Trader):

    def fulfillment(self, allocation_uuid, finish_event):
        """Send app"""

        self.num_outputs = 0
        self.total = len(self.cfg.input_list)
        self.last_input_uuid = ""

        PulsarREST.create_tenant(pulsar_admin_url=self.cfg.pulsar_admin_url,
                                 clusters=self.cfg.clusters,
                                 tenant=self.cfg.user_uuid)

        super(Customer, self).fulfillment(allocation_uuid, finish_event)

        self.checklist_producer = self.market_producer("checklist", MV2.schema.Checklist)

        self.cleanup_producer = self.market_producer("cleanup", MV2.schema.CleanupDataSchema)

        self.output_consumer = self.pulsar_client.subscribe(
            topic=f"persistent://{self.cfg.user_uuid}/{self.cfg.market_uuid}/output_{allocation_uuid}",
            schema=pulsar.schema.AvroSchema(MV2.schema.OutputDataSchema),
            subscription_name=f"{self.cfg.user_uuid}-output_{allocation_uuid}",
            initial_position=pulsar.InitialPosition.Earliest,
            consumer_type=pulsar.ConsumerType.Exclusive,
            message_listener=self.process)

        self.input_producer = self.market_producer("input", MV2.schema.InputDataSchema)

        self.app_producer = self.market_producer("app", MV2.schema.AppSchema)

        app_desc = MV2.schema.AppSchema(
            allocation_uuid=allocation_uuid,
            URI="eiselesr/app", #https://github.com/scope-lab-vu/MODiCuM/blob/master/src/python/modicum/DockerWrapper.py
            RAW=("Application").encode('utf-8'),
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
        )

        print(f"\n{self.cfg.user_uuid}; pid:{os.getpid()}; send app on {self.cfg.user_uuid}/{self.cfg.market_uuid}/app_{allocation_uuid}\n")
        self.app_producer.send(app_desc)

        input_uuid = ""
        while self.num_inputs < self.total:

            now = datetime.datetime.now(tz=datetime.timezone.utc)
            input_uuid = uuid.uuid4().hex
            input = self.cfg.input_list[self.num_inputs]

            input_msg = MV2.schema.InputDataSchema(
                value=input,
                timestamp=now.timestamp(),
                msgnum=self.num_inputs,
                input_uuid=input_uuid
            )

            self.num_inputs = self.num_inputs + 1
            cprint(f"{self.cfg.user_uuid} send message: {self.num_inputs}", "blue")

            self.input_producer.send(input_msg)
            sys.stdout.flush()

        self.last_input_uuid = input_uuid
        print(f"last_input_uuid: {self.last_input_uuid}\n")
            # time.sleep(1)

        print("Customer is Waiting")
        finish_event.wait()
        print("Customer is Done Waiting")


        hash_commit_list_outputs = []
        for output in self.cfg.check_list:
            hash1 = hashlib.sha256(str(output).encode("utf-8"))
            # single hashed outputs to send to Supplier
            hash_commit_list_outputs.append(hash1.hexdigest())

        checklist_msg = MV2.schema.Checklist(
            allocation_uuid = self.allocation_uuid,
            checklist = hash_commit_list_outputs,
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
        )

        cprint(f"{self.cfg.user_uuid} send checklist", "blue")
        self.checklist_producer.send(checklist_msg)

        cprint(f"Make customer sleep. Maybe then it will ack everything")
        # Somthing weird happens here. I sometimes get the last output message
        # but not all of them get acknowleged so when I run again it re-receives them.
        # Why aren't they being acknowledged fast enough?
        for i in range(1):
            time.sleep(1)
            cprint(f"sleeping {i}", "blue")


    def process(self, consumer, msg):
        # TODO: send data to app for processing
        consumer.acknowledge_cumulative(msg)

        self.num_outputs = self.num_outputs + 1
        cprint(f"\n{self.cfg.user_uuid} Process output message: {self.num_outputs}; value:{msg.value()}\n", "blue")

        # TODO: convert to time based?
        # TODO: Move to allocator?
        last = msg.value().input_uuid == self.last_input_uuid
        cprint(f"\n{msg.value().input_uuid}=={self.last_input_uuid}: {last}\n num_ouputs:{self.num_outputs}", "blue")
        if last:
            print("\nAll outputs recieved. Call cleanup\n")
            cleanup = MV2.schema.CleanupDataSchema(
                cleanup=True,
                timestamp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
            )
            self.cleanup_producer.send(cleanup)

        sys.stdout.flush()

    def sign(self, allocation_uuid):

        cprint(f" {self.cfg.user_uuid} Signing", "blue")
        hash1 = hashlib.sha256(str(self.cfg.commit_list).encode("utf-8")).hexdigest()
        hash_commitlist = hashlib.sha256(hash1.encode("utf-8")).hexdigest()
        cprint(f"{self.cfg.user_uuid}; \n hash1: {hash1}; \n commit: {hash_commitlist}", "blue")
        self.pulsar_sign(hash_commitlist, allocation_uuid)
        # TODO: Commit to ledger
        # TODO: Sign on ledger
        # self.ledger_client.customerSign(hash_commitlist)

    def pulsar_sign(self, hash_commitlist, allocation_uuid):
        # TODO: Send commit message to Verifier

        # TODO: Commit to ledger
        # TODO: Sign on ledger
        self.ledger_client.customerSign(allocation_uuid, self.cfg.user_uuid, hash_commitlist)
