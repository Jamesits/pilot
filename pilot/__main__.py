#!/usr/bin/env python3
import logging
import os

from flask import Response
from gevent.pywsgi import WSGIServer

from pilot import create_app
from pilot.args import parse_args
from pilot.utils import find_first_existing_file

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s|%(name)-26s[%(levelname)s] %(message)s'
)

args = parse_args()

user_config_file_path: str = args.config
if len(user_config_file_path) == 0:
    user_config_file_path = find_first_existing_file([
        # *nix
        "/etc/pilot/pilot.conf",
        # Windows
        os.path.join(os.environ.get('LOCALAPPDATA', ''), "pilot", "pilot.conf"),
        os.path.join(os.environ.get('APPDATA', ''), "pilot", "pilot.conf"),
        os.path.join(os.environ.get('PROGRAMDATA', ''), "pilot", "pilot.conf"),
        # current dir
        os.path.join(os.getcwd(), "pilot.conf"),
        # config file located at the root of project directory
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "pilot.conf"),
    ])
if len(user_config_file_path) == 0:
    logger.error("Unable to find a config file, please manually set --config command line argument")
    raise SystemExit(-1)

# note: Flask searches files with relative paths under module path, so we just get the correct absolute path first
app = create_app(os.path.abspath(user_config_file_path))


@app.route("/")
def __placeholder():
    return Response("Segmentation fault (core dumped)", status=500)


@app.after_request
def __after_request_hook(response):
    response.headers["Server"] = "Microsoft-IIS/7.0"
    return response


def main() -> None:
    """Self-contained HTTP server"""
    ip: str = app.config['HTTP_SERVER_LISTEN_IP']
    port: int = int(app.config['HTTP_SERVER_LISTEN_PORT'])
    logger.info(f"Pilot built-in HTTP server started at {ip}:{port}")
    http_server = WSGIServer((ip, port), app)
    http_server.serve_forever()


if __name__ == "__main__":
    main()