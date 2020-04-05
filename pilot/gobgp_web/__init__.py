"""
The recipes Blueprint handles the creation, modification, deletion,
and viewing of recipes for this application.
"""
import logging
from ipaddress import ip_network

from flask import Blueprint, render_template, request, Response
from flask import current_app as app

from pilot.gobgp_web import gobgp_connector
from pilot.gobgp_web.gobgp_json_result_encoder import GoBgpResultEncoder

logger = logging.getLogger(__name__)
default_encoder = GoBgpResultEncoder(ensure_ascii=False, sort_keys=True, indent=4 * ' ')
gobgp_web_blueprint = Blueprint('gobgp_web', __name__, template_folder='templates')


@gobgp_web_blueprint.route('/')
def index():
    routes = gobgp_connector.convert_protobuf_to_dict(gobgp_connector.get_routes())

    # preprocess the routes for display
    cooked_routes = []
    for route in routes:
        destination = route['destination']
        for path in destination['paths']:
            cooked_route = {
                "display_selector": destination['prefix'],
            }

            # get traffic selector
            rules_count = len(path['nlri']['rules'])
            if rules_count == 0:
                logger.warning(f"no rules")
            else:
                if rules_count != 1:
                    logger.warning(f"rules_count={rules_count}")
                rule = path['nlri']['rules'][0]
                ip_ver = 6 if ':' in rule['prefix'] else 4
                cooked_route['ip_ver'] = ip_ver
                if (ip_ver == 6 and rule['prefix_len'] == 128) or (ip_ver == 4 and rule['prefix_len'] == 32):
                    cooked_route['network'] = rule['prefix']
                else:
                    cooked_route['network'] = f"{rule['prefix']}/{rule['prefix_len']}"
                # TODO: support rule['offset']

            # get action
            # currently only support route target -- naive implementation
            for pattr in path['pattrs']:
                if pattr['__descriptor_full_name'] == "gobgpapi.ExtendedCommunitiesAttribute":
                    comm = pattr['communities'][0]['string']
                    cooked_route['community'] = comm
                    for rule in app.config['rule']:
                        if rule.get('route_target', None) == comm:
                            cooked_route['rule_display_name'] = rule['display_name']

            cooked_routes.append(cooked_route)

    # sort it to make the list stable
    cooked_routes.sort(key=lambda x: str(x['ip_ver']) + x['network'])

    # find ourselves
    current_rule = "default"
    for cooked_route in cooked_routes:
        if request.remote_addr == cooked_route['network']:
            current_rule = cooked_route.get('rule_display_name', cooked_route.get('community'))

    return render_template(
        'gobgp_web/index.html',
        ip=request.remote_addr,
        current_rule=current_rule,
        rules=app.config['rule'],
        cooked_routes=cooked_routes,
    )


@gobgp_web_blueprint.route('/peer')
def peer():
    ret = gobgp_connector.get_peers()
    return Response(default_encoder.encode(ret), mimetype='application/json')


@gobgp_web_blueprint.route('/flow')
def flow():
    ret = gobgp_connector.get_routes()
    return Response(default_encoder.encode(ret), mimetype='application/json')


@gobgp_web_blueprint.route('/flow/self', methods=['DELETE'])
def flow_self_delete():
    logger.info(f"/flow/self delete: {request.remote_addr}")
    gobgp_connector.del_route(source_ip=ip_network(request.remote_addr))
    return '', 204


@gobgp_web_blueprint.route('/flow/self', methods=['POST'])
def flow_self_select():
    selected_rule_id = int(request.values['rule'])
    logger.info(f"/flow/self select: {request.remote_addr} => {selected_rule_id}")
    new_route = {
        'source_ip': ip_network(request.remote_addr),
    }
    if 'route_target' in app.config['rule'][selected_rule_id]:
        new_route['route_target'] = app.config['rule'][selected_rule_id]['route_target']
    gobgp_connector.add_route(**new_route)
    return '', 204

# for testing only
# @gobgp_web_blueprint.route('/add')
# def add_path():
#     gobgp_connector.add_route(source_ip=ip_network("10.0.0.1"), route_target="100:100")
#     return ""
#
#
# @gobgp_web_blueprint.route('/del')
# def del_path():
#     gobgp_connector.del_route(source_ip=ip_network("10.0.0.1"))
#     return ""
