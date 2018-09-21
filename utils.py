################################################################################
########################### Loading Configuration Files ########################
################################################################################

import yaml


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



if __name__ == '__main__':
    a = load_yml_config()
    print(a.access_id)