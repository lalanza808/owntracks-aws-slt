# owntracks-aws-slt

Serverless location tracking HTTP endpoints for use with [Owntracks](https://owntracks.org). Uses several [AWS](https://aws.amazon.com) services:

* **API Gateway** - Provides HTTP endpoints to point Owntracks client at
* **Lambda** - Processes incoming data streams and performs queries, cleanups, notifications, etc
* **S3** - Stores incoming messages

The backend code is written in Python 3.6 and makes use of the [Pyramid](https://pylonsproject.org) web framework.

Everything is deployed and managed using the [Zappa](https://github.com/Miserlou/Zappa) serverless management framework.

## Requirements

Before you can use this tool, you must have these prerequisites:

* [Amazon Web Services account](https://aws.amazon.com/free/)
* [Administrative IAM API key pair](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html) configured on your computer
* [Pipenv](https://pipenv.readthedocs.io/en/latest/) installed on your computer
* Python 3.6 installed on your computer (I use [pyenv](https://github.com/pyenv/pyenv))

## Setup

Assuming you have all the requirements met, the following steps will create everything needed:

```bash
$ git clone https://github.com/lalanza808/owntracks-aws-slt.git
$ cd owntracks-aws-slt
$ pipenv install --python 3.6
$ pipenv shell
$ zappa init
$ zappa deploy
```

The Zappa output should provide you with an endpoint for API Gateway - the HTTP endpoints with Python Lambda scripts being triggered behind them.
