from abc import ABCMeta
from ipaddress import IPv4Network, IPv6Network
from typing import Union, Sequence

from google.protobuf.any_pb2 import Any

from pilot.gobgp_interface import attribute_pb2


def pack_nlris(*args: 'NetworkLayerReachabilityInformation') -> Any:
    ret = Any()
    ret.Pack(attribute_pb2.FlowSpecNLRI(
        rules=[x.packed() for x in args]
    ))
    return ret


class NetworkLayerReachabilityInformation(metaclass=ABCMeta):
    nlri_type: int

    def __init__(self: "NetworkLayerReachabilityInformation", nlri_type: int) -> None:
        self.nlri_type = nlri_type

    def packed(self) -> Any:
        raise NotImplementedError


class FlowSpecIpPrefix(NetworkLayerReachabilityInformation):
    network: Union[IPv4Network, IPv6Network]
    offset: int

    def __init__(self: "FlowSpecIpPrefix", nlri_type: int, network: Union[IPv4Network, IPv6Network],
                 offset: int = 0) -> None:
        super().__init__(nlri_type=nlri_type)
        self.network = network
        self.offset = offset

    def packed(self) -> Any:
        assert (self.nlri_type in (1, 2))
        ret = Any()
        ret.Pack(attribute_pb2.FlowSpecIPPrefix(
            type=self.nlri_type,
            prefix=self.network.network_address.exploded,
            prefix_len=self.network.prefixlen,
            offset=self.offset,
        ))
        return ret


class FlowSpecComponent(NetworkLayerReachabilityInformation):
    rules: Sequence[Sequence[int]]

    def __init__(self: "FlowSpecComponent", nlri_type: int, rules: Sequence[Sequence[int]]) -> None:
        super().__init__(nlri_type=nlri_type)
        self.rules = rules

    def packed(self) -> Any:
        assert (self.nlri_type in range(3, 13))
        packed_rules = []
        for op, value in self.rules:
            packed_rules.append(attribute_pb2.FlowSpecComponentItem(
                op=op,
                value=value,
            ))
        ret = Any()
        ret.Pack(attribute_pb2.FlowSpecComponent(
            type=self.nlri_type,
            items=packed_rules,
        ))
        return ret
