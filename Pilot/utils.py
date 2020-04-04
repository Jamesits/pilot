import os
import typing


def find_first_existing_file(f_list: typing.List[str]) -> str:
    for f in f_list:
        if os.path.isfile(f):
            return f
    return ""
