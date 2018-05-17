from collections import namedtuple

Task = namedtuple("Task", ["name", "pull", "pushes"])
Pull = namedtuple("Pull", ["instance"])
Push = namedtuple("Push", ["instance", "selector"])
