import json
import owntracker.config as app_config


bucket_name = app_config.backend['s3']['name']

class Owntracks(object):
    def __init__(self, json_body):
        """User supplies a JSON body and we verify
        it is Owntracks app data.

        Can generate responses in different formats.
        """

        # The glorious "verification" of Owntracks data
        if "_type" not in json_body:
            # TODO better logging
            print("[DEBUG] Not a valid Owntracks JSON object")
            exit(1)

        self.schema_type = json_body["_type"]
        self.schema = schemas[self.schema_type]
        self.data = {}

        required_keys = sorted(self.schema)
        returned_keys = sorted(json_body)

        # Generate new emptied dict object from default schema
        for key in required_keys:
            self.data[key] = ""
        # Overwrite with the values we have
        for key in returned_keys:
            self.data[key] = json_body[key]

        print("[DEBUG] Generating new object: {}".format(self.data))


    def to_json(self):
        return json.dumps(self.data)


    def to_csv(self):
        """Convert the JSON object to CSV"""
        csv_data = []
        for key in sorted(self.data):
            csv_data.append(str(self.data[key]))

        output = ",".join(csv_data)
        return output


    def generate_athena_query(self):
        """Do stuff"""
        table_tmpl = "`{name}` {type}"
        table_columns = []
        # table_columns = ""

        for key, value in self.schema.items():
            # table_columns += table_tmpl.format(
            #     name=key, type=value
            # )
            table_columns.append(table_tmpl.format(
                name=key, type=value
            ))

        query = create_table.format(
            bucket_name=bucket_name,
            table=self.schema_type,
            table_columns=",\n".join(table_columns)
        )

        return str(query)

schemas = {
    "location": {
        "_type": "string",
        "acc": "int",
        "alt": "int",
        "batt": "int",
        "cog": "int",
        "conn": "string",
        "cp": "string",
        "datestamp": "string",
        "device_name": "string",
        "inregions": "string",
        "lat": "double",
        "lon": "double",
        "p": "double",
        "rad": "int",
        "t": "string",
        "tid": "string",
        "timestamp": "int",
        "topic": "string",
        "tst": "int",
        "vac": "int",
        "vel": "int"
    },
    "beacon": {},
    "card": {},
    "cmd": {},
    "configuration": {},
    "encrypted": {},
    "lwt": {},
    "steps": {},
    "transition": {
        "acc": "double",
        "desc": "string",
        "event": "string",
        "lat": "double",
        "lon": "double",
        "t": "string",
        "tid": "string",
        "tst": "int",
        "wtst": "int"
    },
    "waypoint": {
        "desc": "string",
        "lat": "double",
        "lon": "double",
        "major": "int",
        "minor": "int",
        "rad": "int",
        "tst": "int",
        "uuid": "string"
    },
    "waypoints": {}
}

create_table = """
CREATE EXTERNAL TABLE `{bucket_name}-{table}`(
    {table_columns}
)

ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
STORED AS INPUTFORMAT
  'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://{bucket_name}/{table}/'
"""
