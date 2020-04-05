# https://gist.github.com/iwaseyusuke/df1e0300221b0c6aa1a98fc346621fdc
from pilot.gobgp_interface import gobgp_pb2, attribute_pb2, capability_pb2


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
