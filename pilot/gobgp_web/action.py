from abc import ABCMeta
from ipaddress import IPv4Address, IPv6Address, ip_address
from typing import Union, Tuple

from google.protobuf.any_pb2 import Any

from pilot.gobgp_interface import attribute_pb2


def string_to_route_target(i: str) -> Tuple[Union[int, IPv4Address, IPv6Address], int]:
    """
    Route Target from string form to int/ip_address:int form.
    :param i: string
    :return: global_admin, local_admin
    """
    global_admin_pre, local_admin_pre = i.rsplit(":", maxsplit=1)

    if "." in global_admin_pre or ":" in global_admin_pre:
        global_admin = ip_address(global_admin_pre)
    else:
        global_admin = int(global_admin_pre)

    local_admin = int(local_admin_pre)

    return global_admin, local_admin


def pack_actions(*args: 'Action') -> attribute_pb2.ExtendedCommunitiesAttribute:
    return attribute_pb2.ExtendedCommunitiesAttribute(
        communities=[x.packed() for x in args]
    )


class Action(metaclass=ABCMeta):
    def packed(self: 'Action') -> Any:
        raise NotImplementedError


class RateLimitAction(Action):
    rate: float

    def __init__(self: 'RateLimitAction', rate: float):
        super().__init__()
        self.rate = rate

    def packed(self: 'RateLimitAction') -> Any:
        action = Any()
        action.Pack(attribute_pb2.TrafficRateExtended(rate=self.rate))
        return action


# RedirectTwoOctetAsSpecificExtended
# RedirectIPv4AddressSpecificExtended
# RedirectFourOctetAsSpecificExtended
# RedirectIPv6AddressSpecificExtended ???
class RedirectAction(Action):
    global_admin: Union[int, IPv4Address, IPv6Address]
    local_admin: int

    def __init__(self: 'RedirectAction', global_admin: Union[int, IPv4Address, IPv6Address], local_admin: int):
        super().__init__()
        self.global_admin = global_admin
        self.local_admin = local_admin

    def packed(self: 'RedirectAction') -> Any:
        ret = Any()
        action = None
        if isinstance(self.global_admin, int):
            assert self.global_admin < 4294967296
            if self.global_admin < 65536:
                # 2-byte asn
                action = attribute_pb2.RedirectTwoOctetAsSpecificExtended(
                    local_admin=self.local_admin,
                )
                setattr(action, 'as', self.global_admin)  # fuck Python
            else:
                # 4-byte asn
                action = attribute_pb2.RedirectFourOctetAsSpecificExtended(
                    local_admin=self.local_admin,
                )
                setattr(action, 'as', self.global_admin)  # fuck Python
        elif isinstance(self.global_admin, IPv4Address):
            # IPv4
            action = attribute_pb2.RedirectIPv4AddressSpecificExtended(
                address=self.global_admin.exploded,
                local_admin=self.local_admin
            )
        elif isinstance(self.global_admin, IPv6Address):
            # IPv6, I've never heard of this one actually
            action = attribute_pb2.RedirectIPv6AddressSpecificExtended(
                address=self.global_admin.exploded,
                local_admin=self.local_admin
            )
        else:
            raise NotImplementedError("Unknown Global Administrator type")

        ret.Pack(action)
        return ret
