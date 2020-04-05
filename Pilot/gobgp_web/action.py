from abc import ABCMeta

from google.protobuf.any_pb2 import Any

from pilot.gobgp_interface import attribute_pb2


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
