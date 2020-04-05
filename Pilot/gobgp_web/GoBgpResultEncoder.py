from json import JSONEncoder


class GoBgpResultEncoder(JSONEncoder):

    def __init__(self, **kwargs):
        kwargs['ensure_ascii'] = False
        kwargs['sort_keys'] = True
        super().__init__(**kwargs)

    def default(self, o):
        if isinstance(o, bytes):
            return str(o)
        else:
            return super.default(self, o)
