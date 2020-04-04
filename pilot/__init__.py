import os
import site
import typing

from flask import Flask

# for automatic generated GRPC stubs to work
site.addsitedir(os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "gobgp_interface"
))


def create_app(config_filename: typing.Optional[str] = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile(config_filename)
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
    app.register_blueprint(gobgp_web_blueprint, url_prefix="/gobgp")
