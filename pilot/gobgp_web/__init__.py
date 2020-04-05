"""
The recipes Blueprint handles the creation, modification, deletion,
and viewing of recipes for this application.
"""
from ipaddress import ip_network

from flask import Blueprint, render_template, request, Response

from pilot.gobgp_web import gobgp_connector
from pilot.gobgp_web.gobgp_json_result_encoder import GoBgpResultEncoder

default_encoder = GoBgpResultEncoder(ensure_ascii=False, sort_keys=True, indent=4 * ' ')
gobgp_web_blueprint = Blueprint('gobgp_web', __name__, template_folder='templates')


@gobgp_web_blueprint.route('/')
def index():
    routes = gobgp_connector.get_routes()
    return render_template(
        'gobgp_web/index.html',
        ip=request.remote_addr,
        routes=gobgp_connector.convert_protobuf_to_dict(routes),
    )


@gobgp_web_blueprint.route('/add_path')
def addpath():
    gobgp_connector.add_path()
    return ""


@gobgp_web_blueprint.route('/peer')
def peer():
    ret = gobgp_connector.get_peers()
    return Response(default_encoder.encode(ret), mimetype='application/json')


@gobgp_web_blueprint.route('/flow')
def flow():
    ret = gobgp_connector.get_routes()
    return Response(default_encoder.encode(ret), mimetype='application/json')


@gobgp_web_blueprint.route('/add')
def add_path():
    gobgp_connector.add_route(source_ip=ip_network("10.0.0.1"), route_target="100:100")
    return ""


@gobgp_web_blueprint.route('/del')
def del_path():
    gobgp_connector.del_route(source_ip=ip_network("10.0.0.1"))
    return ""
