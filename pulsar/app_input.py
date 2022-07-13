import pulsar
import time

serviceUrl = "pulsar://localhost:6650"
client = pulsar.Client(serviceUrl)

producer = client.create_producer("my-topic")

for i in range(10):
    msg = f"Hello-{i}"
    print(msg)
    producer.send(msg.encode('utf-8'))
    time.sleep(1)

client.close()

