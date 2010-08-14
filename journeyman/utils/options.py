class Options(object):
    @classmethod
    def choices(cls):
        "Return a list of choices"
        return [(text, key) for key, text in cls.__dict__.iteritems() if not key.startswith("_")]