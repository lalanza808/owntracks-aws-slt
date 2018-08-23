#!/usr/bin/env python

from datetime import datetime
from json import dumps
import config as app_config
import boto3
from pprint import pprint

bucket_name = app_config.backend['s3']['name']
bucket_region = app_config.backend['s3']['region']

athena = boto3.client('athena')

query_tmpl = '''
    SELECT
        *
    FROM
        history
    WHERE
        token = '%(token)s'
    AND
        year = %(year)d
    AND
        month = %(month)d
    AND
        day = %(day)d
    ORDER BY
        timestamp asc
'''

response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': 'locations'
        },
        ResultConfiguration={
            'OutputLocation': output_location
        }
    )

print('Execution scheduled with ID -> ', response['QueryExecutionId'])

def ingest(request):
    """Ingest incoming JSON data from Owntracks devices into S3"""
    now = datetime.now()
    device_name = request.matched_route.name

    # https://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html#sec6.1.1
    if request.method == "POST":
        s3 = boto3.client("s3")
        json_data = request.json_body
        json_data["device_name"] = device_name
        s3.put_object(
            ACL="private",
            Body=dumps(json_data),
            Bucket=bucket_name,
            Key="year={}/month={}/day={}/{}.json".format(
                now.year, now.month, now.day, json_data["tst"]
            ),
            ServerSideEncryption='AES256'
        )
        response_code = 202
    else:
        response_code = 204

    return {
        "response": response_code,
        "method": request.method,
        "device": device_name
    }
