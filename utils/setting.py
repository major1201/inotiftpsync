# encoding: utf-8
import yaml

conf = None


def load(stream):
    global conf
    conf = yaml.load(stream)
