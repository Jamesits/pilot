import typing
from collections.abc import Mapping, Sequence


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
