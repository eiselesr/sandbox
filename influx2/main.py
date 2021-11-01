import datetime
import time
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError
import yaml

class TestLogger:
    def __init__(self, influx_config_file):
        with open(influx_config_file, 'r') as stream:
            try:
                db_config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.client = influxdb_client.InfluxDBClient(
            url=db_config["url"],
            token=db_config["token"],
            org=db_config["org"]
        )

        print(db_config)

        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

        p = influxdb_client.Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
        self.write_api.write(bucket=db_config["bucket"],
                             org=db_config["org"],
                             record=p)

        self.query_api = self.client.query_api()
        query = f'from(bucket:"{db_config["bucket"]}")\
        |> range(start: -10m)\
        |> filter(fn:(r) => r._measurement == "my_measurement")\
        |> filter(fn: (r) => r.location == "Prague")\
        |> filter(fn:(r) => r._field == "temperature" )'
        result = self.query_api.query(org=db_config["org"], query=query)
        results = []
        for table in result:
            for record in table.records:
                results.append((record.get_field(), record.get_value()))

        print(results)


        t1 = datetime.datetime.now(tz=datetime.timezone.utc)
        time.sleep(1)
        t2 = datetime.datetime.now(tz=datetime.timezone.utc)

        point1 = {"measurement": "h2o_feet",
                  "tags": {"location": "coyote_creek"},
                  "fields": {"water_level": 2.0},
                  "time": t1}

        point2 = {"measurement": "h2o_feet",
                  "tags": {"location": "coyote_creek"},
                  "fields": {"water_level": 3.0},
                  "time": t2}

        points = [point1, point2]

        self.write_api.write(bucket=db_config["bucket"], org=db_config["org"], record=points)
        #
        query = f'from(bucket:"{db_config["bucket"]}")\
        |> range(start: -10m)\
        |> filter(fn: (r) => r._measurement == "h2o_feet")\
        |> filter(fn: (r) => r.location == "coyote_creek")\
        |> filter(fn: (r) => r._field == "water_level" )'

        result = self.query_api.query(org=db_config["org"],
                                      query=query)

        results = []
        for table in result:
            for record in table.records:
                results.append((record.get_value(), record.get_field()))

        print(results)

TestLogger("./cfg/influxdb_config.yaml")
#
#
#
