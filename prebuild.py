#!/usr/bin/env python

from botocore.client import ClientError
from datetime import datetime
from json import dumps
import config as app_config
import boto3


bucket_name = app_config.backend["s3"]["name"]
bucket_region = app_config.backend["s3"]["region"]
bucket_retention = app_config.backend["s3"]["retention"]
# account_id = boto3.client("sts").get_caller_identity().get("Account")
# glue_role_name = "AWSGlue-{}".format(bucket_name)
# glue_policy_name = "AWSGlue-{}-ReadOnly".format(bucket_name)
# glue_policy_arn = "arn:aws:iam::{account_id}:policy/{policy_name}".format(
#     account_id=account_id,
#     policy_name=glue_policy_name
# )
# glue_managed_policy = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
# glue_assume_policy = {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Principal": {
#                 "Service": "glue.amazonaws.com"
#             },
#             "Action": "sts:AssumeRole"
#         }
#     ]
# }
# glue_custom_policy = {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Action": "s3:Get*",
#             "Resource": "arn:aws:s3:::{}/*".format(bucket_name)
#         }
#     ]
# }


def create_bucket():
    """Create the s3 bucket used for capturing log data if it doesn"t exist already"""
    s3 = boto3.resource("s3")
    s3client = boto3.client("s3")

    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3.create_bucket(
            ACL="private",
            Bucket=bucket_name,
            CreateBucketConfiguration={
                "LocationConstraint": bucket_region
            }
        )
        s3client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration={
                "Rules": [
                    {
                        "Expiration": {
                            "Days": bucket_retention
                        },
                        "Filter": {
                            "Prefix": ""
                        },
                        "ID": "{}-day-retention".format(bucket_retention),
                        "Status": "Enabled"
                    }
                ]
            }
        )

    return


def create_glue_iam():
    """Create the required IAM roles for AWS Glue to assume"""
    iam = boto3.client("iam")
    res = boto3.resource("iam")

    # Ensure IAM role exists
    try:
        res.meta.client.get_role(RoleName=glue_role_name)
        pass
    except ClientError:
        iam.create_role(
            RoleName=glue_role_name,
            AssumeRolePolicyDocument=dumps(glue_assume_policy)
        )

    # Ensure custom IAM policy exists
    try:
        res.meta.client.get_policy(PolicyArn=glue_policy_arn)
        pass
    except ClientError:
        iam.create_policy(
            PolicyName=glue_policy_name,
            PolicyDocument=dumps(glue_custom_policy)
        )

    # Ensure custom Glue policy is attached to role
    try:
        res.meta.client.attach_role_policy(
            RoleName=glue_role_name,
            PolicyArn=glue_policy_arn
        )
        pass
    except ClientError:
        iam.attach_role_policy(
            RoleName=glue_role_name,
            PolicyArn=glue_policy_arn
        )

    # Ensure managed Glue policy is attached to role
    try:
        res.meta.client.attach_role_policy(
            RoleName=glue_role_name,
            PolicyArn=glue_managed_policy
        )
        pass
    except ClientError:
        iam.attach_role_policy(
            RoleName=glue_role_name,
            PolicyArn=glue_managed_policy
        )

    return


def create_glue():
    """Sets up the Glue database and crawler"""
    glue = boto3.client("glue")

    # Ensure Glue database exists
    try:
        glue.get_database(Name=bucket_name)
        pass
    except ClientError:
        glue.create_database(
            DatabaseInput={
                "Name": bucket_name,
                "Description": "Owntracks SLT database"
            }
        )

    # Ensure Glue crawler exists and run it if you create it
    try:
        glue.get_crawler(Name=bucket_name)
        pass
    except ClientError:
        glue.create_crawler(
            Name=bucket_name,
            Description="Owntracks SLT data crawler",
            Role=glue_role_name,
            DatabaseName=bucket_name,
            Targets={
                "S3Targets": [{
                    "Path": "s3://{}/".format(bucket_name)
                }]
            }
        )
        glue.start_crawler(
            Name=bucket_name
        )

    return


def setup():
    print("[+] Setting up S3 bucket resources")
    create_bucket()
    # print("[+] Setting up Glue IAM resources")
    # create_glue_iam()
    # print("[+] Setting up Glue resources")
    # create_glue()
