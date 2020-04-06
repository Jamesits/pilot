import logging
import string
import typing
from collections.abc import Mapping, Sequence
from ipaddress import ip_address
from json import JSONEncoder

from google.protobuf.any_pb2 import Any
from google.protobuf.pyext._message import RepeatedCompositeContainer, RepeatedScalarContainer

from pilot.gobgp_interface import gobgp_pb2, attribute_pb2, capability_pb2

logger = logging.getLogger(__name__)


# https://gist.github.com/iwaseyusuke/df1e0300221b0c6aa1a98fc346621fdc
def unmarshal_any(any_msg):
    """
    Unpacks an `Any` message.
    If need to unpack manually, the following is a simple example::
        if any_msg.Is(attribute_pb2.IPAddressPrefix.DESCRIPTOR):
            ip_addr_prefix = attribute_pb2.IPAddressPrefix()
            any_msg.Unpack(ip_addr_prefix)
            return ip_addr_prefix
    """
    if any_msg is None:
        return None

    # Extract 'name' of message from the given type URL like
    # 'type.googleapis.com/type.name'.
    msg_name = any_msg.type_url.split('.')[-1]

    for pb in (gobgp_pb2, attribute_pb2, capability_pb2):
        msg_cls = getattr(pb, msg_name, None)
        if msg_cls is not None:
            break
    assert msg_cls is not None

    msg = msg_cls()
    any_msg.Unpack(msg)
    return msg


def resolve_protobuf_any_dict(i: dict) -> typing.Any:
    print(i['type_url'])
    return i


def iterate_dict(i: typing.Any) -> typing.Any:
    if isinstance(i, Mapping):
        if 'type_url' in i:
            return resolve_protobuf_any_dict(i)
        else:
            ret = {}
            for k, v in i.items():
                ret[k] = iterate_dict(v)
            return ret

    # dict is Iterable
    if isinstance(i, Sequence) and not isinstance(i, str):
        return [iterate_dict(x) for x in i]

    return i


def protobuf_obj_to_dict(o: any) -> dict:
    assert hasattr(o, 'DESCRIPTOR')

    ret = {
        "__type": o.__class__.__name__,
        "__descriptor_name": o.DESCRIPTOR.name,
        "__descriptor_full_name": o.DESCRIPTOR.full_name,
        "__descriptor_has_options": o.DESCRIPTOR.has_options,
        "__descriptor_is_extendable": o.DESCRIPTOR.is_extendable,
        "__descriptor_syntax": o.DESCRIPTOR.syntax,
    }
    preserved_attributes = []
    preserved_attributes.extend(
        [x for x in dir(o) if
         (not x.startswith("_"))
         and (x[0] not in string.ascii_uppercase)
         and (not callable(getattr(o, x)))
         ]
    )
    for item in preserved_attributes:
        attr = getattr(o, item)
        if isinstance(attr, str) and attr == "<nil>":
            attr = None
        ret[item] = attr
    return ret


def community_to_dict(i: any) -> dict:
    ret = protobuf_obj_to_dict(i)
    ret['local_admin']: i.local_admin
    if hasattr(i, 'as'):
        ret['global_admin'] = str(getattr(i, 'as'))
        ret['asn'] = getattr(i, 'as')
    elif hasattr(i, 'address'):
        ret['address'] = ip_address(getattr(i, 'address'))
        ret['global_admin'] = ret['address'].exploded

    ret['string'] = f"{ret['global_admin']}:{ret['local_admin']}"
    return ret


class GoBgpResultEncoder(JSONEncoder):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def default(self, o):
        if isinstance(o, Any):
            return unmarshal_any(o)

        if isinstance(o, (RepeatedCompositeContainer, RepeatedScalarContainer)):  # this is an iterable
            ret = []
            for item in o:
                ret.append(item)
            return ret

        if isinstance(o, (
                attribute_pb2.RedirectTwoOctetAsSpecificExtended,
                attribute_pb2.RedirectFourOctetAsSpecificExtended,
                attribute_pb2.RedirectIPv4AddressSpecificExtended,
                attribute_pb2.RedirectIPv6AddressSpecificExtended,
        )):  # communities need some custom attributes
            return community_to_dict(o)

        if hasattr(o, 'DESCRIPTOR'):
            return protobuf_obj_to_dict(o)

        if isinstance(o, bytes):
            try:
                return o.decode("utf-8")
            except UnicodeDecodeError:
                logger.warning(f"Unable to decode bytes object {str(o)}")
                return str(o)

        try:
            return super.default(self, o)
        except AttributeError:
            logger.warning(f"Unable to unmarshal type {str(type(o))}")
            return None
