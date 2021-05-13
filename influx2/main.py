# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

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

        print(db_config)
        # self.db_name = db_config['db_name']
        # self.db_drop = db_config['db_drop']
        self.point_values = []
        # try:
        self.client = influxdb_client.InfluxDBClient(
            url=db_config["url"],
            token=db_config["token"],
            org=db_config["org"]
        )

        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

        t1 = datetime.datetime.now(tz=datetime.timezone.utc)
        time.sleep(1)
        t2 = datetime.datetime.now(tz=datetime.timezone.utc)

        self.write_api.write("default", "RIAPS", [{"measurement": "h2o_feet", "tags": {"location": "coyote_creek"},
                                                   "fields": {"water_level": 2.0}, "time": t1},
                                                  {"measurement": "h2o_feet", "tags": {"location": "coyote_creek"},
                                                   "fields": {"water_level": 3.0}, "time": t2}])



        # self.client = InfluxDBClient(host=db_config['db_host'], port=db_config['db_port'],
        #                              database=db_config['db_name'], username=db_config['db_user'],
        #                              password=db_config['db_password'])
        # self.client.switch_database(db_config['db_name'])
        # except:
        #     self.logger.error('database connection failed')
        #     self.client = None


TestLogger("./cfg/influxdb_config.yaml")



