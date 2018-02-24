import os
import configparser

DB_URI="sqlite:///./tmp.db"
CONFIG_PATH=os.path.expanduser("~/.interviewpad.config")
def config_exists():
    return os.path.exists(CONFIG_PATH)
def get_config():
    parser = configparser.RawConfigParser()
    parser.read([CONFIG_PATH,])
    return parser
def save_config(config_parser):
    return config_parser.write(open(CONFIG_PATH,"w"))

COLOR_LIST=["#e6194b","#3cb44b","#ffe119","#0082c8","#f58231","#911eb4","#46f0f0","#f032e6","#d2f53c","#fabebe","#008080","#e6beff","#aa6e28","#fffac8","#800000","#aaffc3","#808000","#ffd8b1","#000080","#808080","#FFFFFF","#000000"]
