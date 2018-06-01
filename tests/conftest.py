import os


def path_to_config(config_name):
    return os.path.join(os.path.dirname(__file__), 'resources/configs', config_name)


def path_to_faces():
    return os.path.join(os.path.dirname(__file__), 'resources/faces')
