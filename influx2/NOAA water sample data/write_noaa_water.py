import datetime
from influxdb_client import InfluxDBClient, WriteApi, WriteOptions
from influxdb_client.client.write_api import ASYNCHRONOUS
import  time
import yaml

class InfluxDBWriter:
    """
    Writer that writes data in batches with 50_000 items.
    """
    def __init__(self):

        with open("cfg/influxdb_config.yaml", 'r') as stream:
            try:
                self.db_config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.client = InfluxDBClient(
            url=self.db_config["url"],
            token=self.db_config["token"],
            org=self.db_config["org"],
            debug=False
        )

        self.write_api = self.client.write_api(write_options=WriteOptions(batch_size=500,
                                                                          flush_interval=10_000,
                                                                          jitter_interval=2_000,
                                                                          retry_interval=5_000,
                                                                          max_retries=5,
                                                                          max_retry_delay=30_000,
                                                                          exponential_base=2))

    def write(self):

        # t = datetime.datetime.utcfromtimestamp(time.time()).isoformat() + 'Z'
        t = datetime.datetime.utcnow()
        self.write_api.write(bucket=self.db_config["bucket"],
                             org=self.db_config["org"],
                             record=[{"measurement": "h2o_feet",
                                      "tags": {"location": "coyote_creek"},
                                      "fields": {"water_level": 1},
                                      "time": t}])

    def run(self):
        i = 0
        while i < 20000:
            self.write()
            i += 1
        self.write_api.close()

if __name__ == '__main__':
    writer = InfluxDBWriter()
    writer.run()
