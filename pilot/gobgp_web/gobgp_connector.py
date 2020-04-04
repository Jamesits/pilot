import sys

from flask import current_app as app

sys.path.append('./gobgp_interface')

import grpc

from pilot.gobgp_interface import gobgp_pb2
from pilot.gobgp_interface import gobgp_pb2_grpc

from protobuf_to_dict import protobuf_to_dict

def get_peers():
    channel = grpc.insecure_channel(f"{app.config['GOBGP_IP']}:{app.config['GOBGP_PORT']}")
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)
    
    peers = stub.ListPeer(gobgp_pb2.ListPeerRequest(), app.config['GOBGP_TIMEOUT_MS'])
    ret = []
    
    for peer in peers:
        peer = peer.peer
        print("BGP neighbor is %s, remote AS %d" % (peer.conf.neighbor_address, peer.conf.peer_as))
        print("  BGP version 4, remote router ID %s" % (peer.state.router_id))
        print("  BGP state = %s, up for %s" % (peer.state.session_state, peer.timers.state.uptime))

        ret.append(protobuf_to_dict(peer))

    return ret

def get_table():
    channel = grpc.insecure_channel(f"{app.config['GOBGP_IP']}:{app.config['GOBGP_PORT']}")
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)
    # table = stub.GetTable(gobgp_pb2.GetTableRequest(
    #     table_type=gobgp_pb2.GLOBAL,
    #     family=gobgp_pb2.Family(
    #         afi =  gobgp_pb2._FAMILY_AFI.values_by_name['AFI_IP'].number,
    #         safi = gobgp_pb2._FAMILY_SAFI.values_by_name["SAFI_FLOW_SPEC_UNICAST"].number,
    #     ),
    #     # name=,
    # ), app.config['GOBGP_TIMEOUT_MS'])

def get_routes():
    channel = grpc.insecure_channel(f"{app.config['GOBGP_IP']}:{app.config['GOBGP_PORT']}")
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    routes = stub.ListPath(gobgp_pb2.ListPathRequest(
        table_type=gobgp_pb2.GLOBAL,
        #name="",
        family=gobgp_pb2.Family(
            afi =  gobgp_pb2._FAMILY_AFI.values_by_name['AFI_IP'].number,
            safi = gobgp_pb2._FAMILY_SAFI.values_by_name["SAFI_FLOW_SPEC_UNICAST"].number,
        ),
    ), app.config['GOBGP_TIMEOUT_MS'])

    ret = []
    for route in routes:
        ret.append(protobuf_to_dict(route))
    
    return ret

