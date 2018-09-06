#!/usr/bin/env python

from datetime import datetime
from json import dumps, loads
from pytz import utc
import config as app_config
import boto3


bucket_name = app_config.backend['s3']['name']
bucket_region = app_config.backend['s3']['region']


def response(code, method, device):
    """Returns a JSON response to HTTP clients"""
    return {
        "response": code,
        "method": method,
        "device": device
    }


def status(request):
    """View status of the device"""
    device_name = request.matched_route.name

    if request.method == "GET":
        s3 = boto3.client("s3")
        object = s3.get_object(
            Bucket=bucket_name,
            Key="current/{}.json".format(device_name)
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
        print("[DEBUG] Received object!\n{}".format(json_data))

        # Put the object in the date stamped path
        s3.put_object(
            ACL="private",
            Body=dumps(json_data),
            Bucket=bucket_name,
            Key="year={}/month={}/day={}/{}_{}.json".format(
                now.year, now.month, now.day,
                json_data["timestamp"], json_data["_type"]
            ),
            ServerSideEncryption='AES256'
        )

        # Also update the "current" object
        if json_data["_type"] == "location":
            s3.put_object(
                ACL="private",
                Body=dumps(json_data),
                Bucket=bucket_name,
                Key="current/{}-status.json".format(device_name),
                ServerSideEncryption='AES256'
            )

        response_code = 202
    else:
        response_code = 204

    return response(response_code, request.method, device_name)
