#!/usr/bin/env python


import json
from os import environ
from secrets import token_urlsafe


project_name = f"{environ['PROJECT']}-{environ['CODENAME']}-{environ['ENV']}"

def init_zappa():
    zappa_settings = {
        "live": {
            "app_function": "owntracker.app.generate_wsgi_app",
            "aws_region": "us-west-2",
            "profile_name": "default",
            "project_name": project_name,
            "runtime": "python3.6",
            "s3_bucket": project_name,
            "keep_warm": False,
            "log_level": "CRITICAL",
            "extra_permissions": [{
                "Effect": "Allow",
                "Action": [
                    "s3:Get*",
                    "s3:Put*"
                ],
                "Resource": [f"arn:aws:s3:::{project_name}"]
            }],
            "tags": {
              "Project": project_name
            },
            "timeout_seconds": 3
        }
    }

    print(json.dumps(zappa_settings))


def init_config():
    devices = {
        "device0": token_urlsafe(16)
    }

    backend = {
        "s3": {
            "name": project_name,
            "region": "us-west-2",
            "retention": 365
        }
    }

    config_body = f"devices = {devices}\n"
    config_body += f"backend = {backend}\n"

    print(config_body)
