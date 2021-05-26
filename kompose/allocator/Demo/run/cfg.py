class Cfg:
    # ip = "172.18.0.2"
    ip = "172.21.20.53"
    port = "8080"
    # ip = "34.75.42.6"
    # port = "80"
    pulsar_url = f"pulsar://{ip}:6650"
    pulsar_admin_url = f"http://{ip}:{port}/admin/v2"
    function_api = f"http://{ip}:{port}/admin/v3/functions"
    presto_host = f"{ip}"
    presto_port = 8081
    tenant = "public"
    namespace = "default"
    logger_topic = "logger"
    deposit = 1000

    clusters = ["standalone"]
    # clusters = ["pulsar-modicum"]


    # MARKET CONFIG
    market_uuid = "market_62"

    # APP CONFIG
    topic = "customer_offers"
    window = 60

    # USER CONFIG
    user_uuid = "customer_1"
    mediators = ["mediator1"]

    # Commit list

    honest_customer = False
    if honest_customer:
        input_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        commit_list = [0, 2, 4, 6, 8]
        check_list = [0, 2, 4, 6, 8]
    else:
        input_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        commit_list = [0, 2, 4, 6, 8]
        check_list = [0, 2, 4, 6]

    def print_msg(self, consumer, msg):
        print(f"subscription_name:{consumer.subscription_name()}")
        # print(f"topic:{consumer.topic()}")
        # print(f"data:{msg.data()}")
        # print(f"event_timestamp:{msg.event_timestamp()}")
        print(f"message_id:{msg.message_id()}")
        # print(f"partition_key:{msg.partition_key()}")
        # print(f"properties:{msg.properties()}")
        # print(f"redelivery_count:{msg.redelivery_count()}")
        print(f"topic_name:{msg.topic_name()}")
        print(f"value:{msg.value()}\n")

    def print_msgvalue(self, msg):
        print("NEW MESSAGE")
        # print(f"subscription_name:{consumer.subscription_name()}")
        # print(f"topic:{consumer.topic()}")
        # print(f"data:{msg.data()}")
        # print(f"event_timestamp:{msg.event_timestamp()}")
        # print(f"message_id:{msg.message_id()}")
        # print(f"partition_key:{msg.partition_key()}")
        # print(f"properties:{msg.properties()}")
        # print(f"redelivery_count:{msg.redelivery_count()}")
        # print(f"topic_name:{msg.topic_name()}")
        print(f"value:{msg}\n")
