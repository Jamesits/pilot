from dataclasses import dataclass
from typing import List, Optional

from google.protobuf.any_pb2 import Any

from pilot.gobgp_interface import gobgp_pb2, attribute_pb2
from pilot.gobgp_web.action import pack_actions, Action
from pilot.gobgp_web.nlri import pack_nlris, NetworkLayerReachabilityInformation


@dataclass
class Path:
    afi: gobgp_pb2.Family
    safi: gobgp_pb2.Family
    origin: int = 0
    actions: Optional[List[Action]] = None
    next_hops: Optional[List[str]] = None
    nlris: List[NetworkLayerReachabilityInformation] = None
    additional_pattrs: Optional[List[Any]] = None  # contains a OriginAttribute, an Action and a MpReachNLRIAttribute

    def next_hop_not_important(self: 'Path'):
        if self.afi == gobgp_pb2.Family.AFI_IP:
            return "0.0.0.0"
        elif self.afi == gobgp_pb2.Family.AFI_IPV6:
            return "::0"
        else:
            raise NotImplementedError("Unknown AFI")

    def get_family(self: 'Path') -> gobgp_pb2.Family:
        return gobgp_pb2.Family(
            afi=self.afi,
            safi=self.safi,
        )

    def get_packed_pattrs(self: 'Path'):
        pattrs = []

        # actions
        if self.actions:
            ac = Any()
            ac.Pack(pack_actions(*self.actions))
            pattrs.append(ac)

        # next hops
        nh = self.next_hops
        if nh is None or len(nh) == 0:
            nh = [self.next_hop_not_important()]

        nh_attribute = Any()
        nh_attribute.Pack(attribute_pb2.MpReachNLRIAttribute(
            family=self.get_family(),
            nlris=[pack_nlris(*self.nlris)],
            next_hops=nh,
        ))
        pattrs.append(nh_attribute)

        # origin
        og = Any()
        og.Pack(attribute_pb2.OriginAttribute(origin=self.origin))
        pattrs.append(og)

        if self.additional_pattrs is not None:
            pattrs.extend(self.additional_pattrs)

        return pattrs

    def packed(self: 'Path') -> gobgp_pb2.Path:
        ret = gobgp_pb2.Path(
            family=self.get_family(),
            nlri=pack_nlris(*self.nlris),
            pattrs=self.get_packed_pattrs(),
            source_asn=self.origin,
        )
        return ret
