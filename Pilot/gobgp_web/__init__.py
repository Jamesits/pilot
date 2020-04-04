"""
The recipes Blueprint handles the creation, modification, deletion,
and viewing of recipes for this application.
"""
from flask import Blueprint
gobgp_web_blueprint = Blueprint('gobgp_web', __name__, template_folder='templates')

from . import routes
