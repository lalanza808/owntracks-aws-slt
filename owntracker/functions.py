#!/usr/bin/env python

import boto3
from pytz import utc
from datetime import datetime
from json import dumps, loads

import owntracker.config as app_config
import owntracker.schema as app_schema


bucket_name = app_config.backend['s3']['name']
bucket_region = app_config.backend['s3']['region']


def response(code, method, device):
    """Returns a JSON response to HTTP clients"""
    return {
        "response": code,
        "method": method,
        "device": device
    }

def index(request):
    return response(200, request.method, None)

def status(request):
    """View status of the device"""
    device_name = request.matched_route.name

    if request.method == "GET":
        s3 = boto3.client("s3")
        object = s3.get_object(
            Bucket=bucket_name,
            Key="live/{}.json".format(device_name)
        )
        json_body = loads(object["Body"].read())
        return json_body
    else:
        return response(204, request.method, device_name)

def ingest(request):
    """Ingest incoming JSON data from Owntracks devices into S3"""
    now = datetime.now(tz=utc)
    device_name = request.matched_route.name

    # https://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html#sec6.1.1
    if request.method == "POST":

        # Discard request if empty body string
        if not request.body:
            return response(400, request.method, device_name)

        # Otherwise continue
        s3 = boto3.client("s3")
        json_data = request.json_body
        json_data["device_name"] = device_name
        json_data["timestamp"] = int(now.timestamp())
        json_data["datestamp"] = now.strftime("%Y-%m-%d %H:%M:%S %Z")

        # Instantiate class to normalize data
        owntracks = app_schema.Owntracks(json_data)

        # Put the object in the date stamped path as CSV object
        s3.put_object(
            ACL="private",
            Body=owntracks.to_csv(),
            Bucket=bucket_name,
            Key="live/{}/{}/{}/{}/{}.csv".format(
                json_data["_type"],
                now.year, now.month, now.day,
                json_data["timestamp"]
            ),
            ServerSideEncryption='AES256'
        )

        # Also put the object in the date stamped path as JSON object
        s3.put_object(
            ACL="private",
            Body=owntracks.to_json(),
            Bucket=bucket_name,
            Key="live/{}/{}/{}/{}/{}.json".format(
                json_data["_type"],
                now.year, now.month, now.day,
                json_data["timestamp"]
            ),
            ServerSideEncryption='AES256'
        )

        # Also update the "current" object
        if json_data["_type"] == "location":
            s3.put_object(
                ACL="private",
                Body=owntracks.to_json(),
                Bucket=bucket_name,
                Key="live/{}-status.json".format(device_name),
                ServerSideEncryption='AES256'
            )

        response_code = 202
    else:
        response_code = 204

    return response(response_code, request.method, device_name)
