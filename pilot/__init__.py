import logging
import os
import site

import toml
from flask import Flask

logger = logging.getLogger(__name__)

# for automatic generated GRPC stubs to work
site.addsitedir(os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "gobgp_interface"
))


def create_app(config_filename: str) -> Flask:
    config = toml.load(config_filename)
    # process the config
    rule_id = 0
    if 'rule' in config:
        for rule in config['rule']:
            rule['id'] = rule_id
            rule_id += 1
    else:
        logger.warning(f"You have no rules defined")
        config['rule'] = []

    app = Flask(__name__, instance_relative_config=False, static_url_path='')
    # app.config.from_pyfile(config_filename)
    app.config.update(config)  # from_object or from_mapping doesn't work here
    initialize_extensions(app)
    register_blueprints(app)
    return app


def initialize_extensions(app: Flask) -> None:
    # Since the application instance is now created, pass it to each Flask
    # extension instance to bind it to the Flask application instance (app)
    pass


def register_blueprints(app: Flask) -> None:
    # Since the application instance is now created, register each Blueprint
    # with the Flask application instance (app)
    from pilot.gobgp_web import gobgp_web_blueprint
    app.register_blueprint(gobgp_web_blueprint, url_prefix="/pilot")
