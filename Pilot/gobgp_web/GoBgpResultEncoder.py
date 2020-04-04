from json import JSONEncoder


class GoBgpResultEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, bytes):
            return str(o)
        else:
            return super.default(self, o)
