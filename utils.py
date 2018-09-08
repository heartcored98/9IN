# ======= Loading Configuration Files ====== #
import hashlib
import yaml
import datetime


class Objdict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


def load_yml_config(filename='settings.yml'):
    with open(filename, 'r') as stream:
        try:
            return Objdict(yaml.load(stream))
        except yaml.YAMLError as exc:
            return None


def hash_attribute(value, level=256):
    str_as_bytes = str.encode(value)
    if level == 256:
        hashed_value = hashlib.sha512(str_as_bytes).hexdigest()
    elif level == 512:
        hashed_value = hashlib.sha256(str_as_bytes).hexdigest()
    else:
        ValueError()
    return hashed_value


def attatch_timestamp(value):
    t = str(datetime.datetime.utcnow().timestamp())
    value = t + str(value)
    return value


if __name__ == '__main__':
    a = load_yml_config()
    print(a.access_id)
