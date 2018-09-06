#!/usr/bin/env python

import functions as lambda_functions
import config as app_config

from wsgiref.simple_server import make_server
from pyramid.view import view_config, view_defaults
from pyramid.config import Configurator
from configparser import ConfigParser
from pathlib import Path


# Generate routes and views and build the app
def configure_app():
    with Configurator() as config:
        # Generate routes for devices
        for device_name in app_config.devices:
            device_key = app_config.devices[device_name]
            config.add_route(
                device_name,
                "/device/{}".format(device_key)
            )
            config.add_route(
                "{}-status".format(device_name),
                "/status/{}".format(device_name)
            )
            config.add_view(
                lambda_functions.ingest,
                route_name=device_name,
                renderer="json"
            )
            config.add_view(
                lambda_functions.status,
                route_name="{}-status".format(device_name),
                renderer="json"
            )
        app = config.make_wsgi_app()
        return app


# API Gateway/Zappa function handler
def generate_wsgi_app(app, environ):
    wsgi_app = configure_app()
    return wsgi_app(app, environ)


# Local web server for development
if __name__ == "__main__":
    print("[+] Starting local web server on port 8080...")
    server = make_server("0.0.0.0", 8080, configure_app())
    server.serve_forever()
