import datetime
import sys

import pulsar
from termcolor import cprint
import MV2.schema

import MV2.helpers.helpers as helper

class Client():
    def __init__(self, cfg):

        self.cfg = cfg

        self.pulsar_client = pulsar.Client(cfg.pulsar_url)

        if not helper.waiting4namespace(self.cfg):
            self.ledger_producer = self.pulsar_client.create_producer(
                topic=f"persistent://{cfg.tenant}/{cfg.market_uuid}/ledger",
                schema=pulsar.schema.AvroSchema(MV2.schema.LedgerSchema))

    # def createAllocation(self, allocation_uuid, customer_uuid, mediator_uuid):
    def createAllocation(self, allocation_uuid, alloc_msg):

        cprint(f"\n{self.cfg.user_uuid} createAllocation alloc_msg.price: {alloc_msg.price}"
               f"\n{self.cfg.user_uuid} createAllocation type(alloc_msg.price): {type(alloc_msg.price)}", "yellow")

        ledger_msg = MV2.schema.LedgerSchema(
            allocation_uuid=allocation_uuid,
            user_uuid=alloc_msg.customer_uuid,
            mediator_uuid=alloc_msg.mediator_uuid,
            function="createAllocation",
            price=alloc_msg.price,
            args=[],
            args_bytes=[b'0'],
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
        )

        cprint(f"\n{self.cfg.user_uuid} send createAllocation to ledger", "yellow")
        sys.stdout.flush()
        self.ledger_producer.send(ledger_msg)
        # self.ledger_producer.send_async(ledger_msg,callback=self.ack_received)
        cprint(f"\n{self.cfg.user_uuid} done sending createAllocation to ledger", "yellow")
        sys.stdout.flush()

    def ack_received(self, res, msg_id):
        cprint(f"uuid: {self.cfg.user_uuid}; ACK RECEIVED: {res}; msg_id: {msg_id}\n", "red", "on_blue")


    def addSupplier(self, allocation_uuid, supplier_uuid):
        ledger_msg = MV2.schema.LedgerSchema(
            allocation_uuid=allocation_uuid,
            user_uuid=supplier_uuid,
            function="addSupplier",
            args=[],
            args_bytes=[b'0'],
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp())

        cprint(f"\n{self.cfg.user_uuid} send addSupplier to ledger", "yellow")
        self.ledger_producer.send(ledger_msg)
        cprint(f"\n{self.cfg.user_uuid} done sending addSupplier to ledger", "yellow")

    def mediatorSign(self, allocation_uuid, user_uuid,):
        cprint(f"\n{self.cfg.user_uuid} Mediator signs the ledger", "yellow")

        ledger_msg = MV2.schema.LedgerSchema(
            allocation_uuid=allocation_uuid,
            user_uuid=user_uuid,
            function="mediatorSign",
            args=[],
            args_bytes=[],
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp())

        self.ledger_producer.send(ledger_msg)

    def customerSign(self, allocation_uuid, user_uuid, hash_commitlist):
        cprint(f"\n{self.cfg.user_uuid} Customer signs the ledger", "yellow")

        ledger_msg = MV2.schema.LedgerSchema(
            allocation_uuid=allocation_uuid,
            user_uuid=user_uuid,
            function="customerSign",
            args=[hash_commitlist],
            args_bytes=[b'0'],
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp())

        self.ledger_producer.send(ledger_msg)


    def supplierSign(self, allocation_uuid, user_uuid,):
        cprint(f"\n{self.cfg.user_uuid} Supplier signs the ledger", "yellow")

        ledger_msg = MV2.schema.LedgerSchema(
            allocation_uuid=allocation_uuid,
            user_uuid=user_uuid,
            function="supplierSign",
            args=[],
            args_bytes=[b'0'],
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp())

        self.ledger_producer.send(ledger_msg)

    def postOutput(self, allocation_uuid, user_uuid, hashed_output_checklist, input_MessageId_list):
        cprint(f"\n{self.cfg.user_uuid} Supplier commits output hash to the ledger", "yellow")
        cprint(f"\n{self.cfg.user_uuid} {input_MessageId_list}", "yellow")


        ledger_msg = MV2.schema.LedgerSchema(
            allocation_uuid=allocation_uuid,
            user_uuid=user_uuid,
            function="postOutput",
            args=[hashed_output_checklist],
            args_bytes=input_MessageId_list,
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp())


        self.ledger_producer.send(ledger_msg)

    def postMediation(self, allocation_uuid, hashed_mediator_output):
        cprint(f"\n{self.cfg.user_uuid} Mediator posts output to the ledger", "yellow")

        ledger_msg = MV2.schema.LedgerSchema(
            allocation_uuid=allocation_uuid,
            user_uuid=self.cfg.user_uuid,
            function="postMediation",
            args=[hashed_mediator_output],
            args_bytes=[],
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp())

        self.ledger_producer.send(ledger_msg)


