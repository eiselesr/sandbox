import multiprocessing

import MV2.allocator
import MV2.helpers.PulsarREST as PulsarREST

import cfg
# import actor_sim

# def sim_listener():
#     pass

cfg0 = cfg.Cfg()
# register tenant and namespace with Pulsar
# THIS WILL GO INTO THE ALLOCATOR OR IN A SETUP SCRIPT
PulsarREST.create_tenant(pulsar_admin_url=cfg0.pulsar_admin_url,
                         clusters=cfg0.clusters,
                         tenant=cfg0.tenant)
PulsarREST.create_namespace(pulsar_admin_url=cfg0.pulsar_admin_url,
                            tenant=cfg0.tenant,
                            namespace=cfg0.market_uuid)

cfg0.user_uuid = "allocator_1"
# alloc = MV2.allocator.Allocator(cfg0)
# finish_event = multiprocessing.Event()

# pulsar_client = pulsar.Client(cfg.pulsar_url)
# sim_consumer = pulsar_client.subscribe(
#             topic=f"persistent://{cfg.tenant}/{cfg.market_uuid}/simulation",
#             schema=pulsar.schema.AvroSchema(MV2.schema.AllocationSchema),
#             subscription_name=f"{cfg.user_uuid}-simulation-subscription",
#             initial_position=pulsar.InitialPosition.Latest,
#             consumer_type=pulsar.ConsumerType.Exclusive,
#             message_listener=sim_listener)

try:
    allocator = multiprocessing.Process(target=MV2.allocator.Allocator,
                                        args=(cfg0,))
    print(f"Start simulated {cfg0.user_uuid} user")
    allocator.start()

    allocator.join()

    print(f"Close simulated {cfg0.user_uuid} user")
except Exception as e:
    print(f"failed for some reason: {e}")







