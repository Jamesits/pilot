#################
#### imports ####
#################

from flask import render_template, request, Response
from flask import current_app as app
from . import gobgp_web_blueprint
from . import gobgp_connector
# import simplejson as json

# from simplejson import JSONEncoder
from json import JSONEncoder
class GoBgpResultEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            return str(o)
        else:
            return super.default(self, o)

default_encoder = GoBgpResultEncoder(ensure_ascii=False, sort_keys=True, indent=4 * ' ')

################
#### routes ####
################

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