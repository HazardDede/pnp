import os


def resource_path(path):
    return os.path.join(os.path.dirname(__file__), path)


def path_to_config(config_name):
    return os.path.join(os.path.dirname(__file__), 'resources/configs', config_name)


def path_to_faces():
    return os.path.join(os.path.dirname(__file__), 'resources/faces')
