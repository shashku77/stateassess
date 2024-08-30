"""Manages disk space drive configfile.

Saves config.yaml in local repository.
"""


import yaml
import io
import logging
import streamlit as st
from yaml.loader import SafeLoader

CONFIG_FN = "config.yaml"

#def dump_dict_to_yaml_stringio(config):
#    """Dump the dictionary to a YAML format string"""
#    yaml_str = yaml.dump(config)
#    return io.StringIO(yaml_str)


def get_config_data():
    """Get the config from disk."""
    with open('./config.yaml','r') as file:
        config = yaml.load(file, Loader=SafeLoader)
        file.close
    return config


def save_config_data(config):
     
    with open('./config.yaml','w') as file:
        data = yaml.dump(config, file, sort_keys=False)
        file.close