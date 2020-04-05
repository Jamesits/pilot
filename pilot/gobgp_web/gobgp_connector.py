# https://blog.balus.xyz/entry/2019/10/18/010000
import json
import logging
import typing
from ipaddress import IPv4Network, IPv6Network, IPv4Address, IPv6Address

import grpc
from flask import current_app as app
from protobuf_to_dict import protobuf_to_dict

from pilot.gobgp_interface import gobgp_pb2, gobgp_pb2_grpc
from pilot.gobgp_web.action import string_to_route_target, RedirectAction
from pilot.gobgp_web.gobgp_json_result_encoder import GoBgpResultEncoder
from pilot.gobgp_web.nlri import FlowSpecIpPrefix
from pilot.gobgp_web.path import Path

# We can use MessageToDict but it'll throw exception for Any
# from google.protobuf.json_format import MessageToDict

logger = logging.getLogger(__name__)


def connection_factory() -> gobgp_pb2_grpc.GobgpApiStub:
    gobgp_ip = app.config['gobgp']['address']
    gobgp_port = app.config['gobgp']['port']
    channel = grpc.insecure_channel(f"{gobgp_ip}:{gobgp_port}")
    stub = gobgp_pb2_grpc.GobgpApiStub(channel)
    return stub


def convert_protobuf_to_dict(i: typing.Any) -> dict:
    return json.loads(GoBgpResultEncoder().encode(i))


def get_afi(ip: typing.Union[IPv4Address, IPv4Network, IPv6Address, IPv6Network]) -> int:
    if isinstance(ip, IPv4Network) or isinstance(ip, IPv4Address):
        return gobgp_pb2.Family.AFI_IP
    elif isinstance(ip, IPv6Network) or isinstance(ip, IPv6Address):
        return gobgp_pb2.Family.AFI_IPV6
    else:
        raise NotImplementedError("Unknown AFI")


def get_peers() -> typing.List:
    stub = connection_factory()

    peers = stub.ListPeer(gobgp_pb2.ListPeerRequest(), app.config['GOBGP_TIMEOUT_MS'])
    ret = []

    for peer in peers:
        peer = peer.peer
        logger.info(
            f"neighbor_ip={peer.conf.neighbor_address}, remote_as={peer.conf.peer_as}, "
            f"remote_id={peer.state.router_id}, session_state={peer.state.session_state}, "
            # uptime is a Timestamp https://googleapis.dev/python/protobuf/latest/google/protobuf/timestamp_pb2.html
            f"uptime={str(peer.timers.state.uptime.ToSeconds())}s"
        )
        ret.append(protobuf_to_dict(peer))

    return ret


# def get_table():
#     stub = connection_factory()
# table = stub.GetTable(gobgp_pb2.GetTableRequest(
#     table_type=gobgp_pb2.GLOBAL,
#     family=gobgp_pb2.Family(
#         afi =  gobgp_pb2._FAMILY_AFI.values_by_name['AFI_IP'].number,
#         safi = gobgp_pb2._FAMILY_SAFI.values_by_name["SAFI_FLOW_SPEC_UNICAST"].number,
#     ),
#     # name=,
# ), gobgp_connection_timeout_ms)


def get_routes() -> typing.List[gobgp_pb2.ListPathResponse]:
    stub = connection_factory()

    # IPv4
    ret4 = []
    routes = stub.ListPath(gobgp_pb2.ListPathRequest(
        table_type=gobgp_pb2.GLOBAL,
        # name="",
        family=gobgp_pb2.Family(
            afi=gobgp_pb2.Family.AFI_IP,
            safi=gobgp_pb2.Family.SAFI_FLOW_SPEC_UNICAST,
        ),
    ), app.config['gobgp']['timeout_ms'])
    for route in routes:
        ret4.append(route)

    # IPv6
    ret6 = []
    routes = stub.ListPath(gobgp_pb2.ListPathRequest(
        table_type=gobgp_pb2.GLOBAL,
        # name="",
        family=gobgp_pb2.Family(
            afi=gobgp_pb2.Family.AFI_IP6,
            safi=gobgp_pb2.Family.SAFI_FLOW_SPEC_UNICAST,
        ),
    ), app.config['gobgp']['timeout_ms'])
    for route in routes:
        ret6.append(route)

    return ret4 + ret6


def add_route(source_ip: typing.Union[IPv4Network, IPv6Network], route_target: str) -> None:
    stub = connection_factory()
    global_admin, local_admin = string_to_route_target(route_target)

    new_path = Path(
        afi=get_afi(source_ip),
        safi=gobgp_pb2.Family.SAFI_FLOW_SPEC_UNICAST,
        nlris=[
            FlowSpecIpPrefix(nlri_type=2, network=source_ip),
        ],
        actions=[
            RedirectAction(global_admin=global_admin, local_admin=local_admin)
        ]
    )

    stub.AddPath(
        gobgp_pb2.AddPathRequest(
            table_type=gobgp_pb2.GLOBAL,
            path=new_path.packed(),
        ),
        timeout=app.config['gobgp']['timeout_ms'],
    )


def del_route(source_ip: typing.Union[IPv4Network, IPv6Network]) -> None:
    """
    Delete all the routes attached to the source IP
    :param source_ip:
    :return:
    """
    stub = connection_factory()

    new_path = Path(
        afi=get_afi(source_ip),
        safi=gobgp_pb2.Family.SAFI_FLOW_SPEC_UNICAST,
        nlris=[
            FlowSpecIpPrefix(nlri_type=2, network=source_ip),
        ],
    )

    stub.DeletePath(
        gobgp_pb2.DeletePathRequest(
            table_type=gobgp_pb2.GLOBAL,
            path=new_path.packed(),
        ),
        timeout=app.config['gobgp']['timeout_ms'],
    )
