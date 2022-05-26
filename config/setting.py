import configparser
import os


def get_param(name):
    conf  = os.environ.get(name)
    if conf:
        return conf
    else :
        config = configparser.ConfigParser()
        try:
            config.read("config/config.ini")
            return config['SETTING'][name]
        except Exception :
            return None
            #config.read(os.environ.get('PROXY_PATH_SETTING'))
            #return config['SETTING'][name]
