"""
The recipes Blueprint handles the creation, modification, deletion,
and viewing of recipes for this application.
"""
from flask import Blueprint, render_template, request, Response

from pilot.gobgp_web import gobgp_connector
from pilot.gobgp_web.GoBgpResultEncoder import GoBgpResultEncoder

default_encoder = GoBgpResultEncoder(ensure_ascii=False, sort_keys=True, indent=4 * ' ')
gobgp_web_blueprint = Blueprint('gobgp_web', __name__, template_folder='templates')


@gobgp_web_blueprint.route('/')
def index():
    routes = gobgp_connector.get_routes()
    print(routes)
    return render_template('gobgp_web/index.html', **{
        "ip": request.remote_addr,
        "routes": routes,
    })


@gobgp_web_blueprint.route('/add_path')
def addpath():
    gobgp_connector.add_path()
    return ""


@gobgp_web_blueprint.route('/peer')
def peer():
    ret = gobgp_connector.get_peers()
    # import ipdb; ipdb.set_trace()
    return Response(default_encoder.encode(ret), mimetype='application/json')


@gobgp_web_blueprint.route('/flow')
def flow():
    return Response(default_encoder.encode({
        "fuck": "shit"
    }), mimetype='application/json')
