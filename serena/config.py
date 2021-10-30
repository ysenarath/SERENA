import configparser
from os.path import join, exists, dirname, abspath

PROJECT_PATH = abspath(join(dirname(abspath(__file__)), '..'))

ENVIRONMENT = 'production'
CONFIG_PATH = join(PROJECT_PATH, 'config.prod.ini')

if not exists(CONFIG_PATH):
    ENVIRONMENT = 'development'
    CONFIG_PATH = join(PROJECT_PATH, 'config.dev.ini')

if not exists(CONFIG_PATH):
    ENVIRONMENT = 'default'
    CONFIG_PATH = join(PROJECT_PATH, 'config.ini')

config = configparser.ConfigParser()
config.read(CONFIG_PATH)

config['DEFAULT']['project_path'] = PROJECT_PATH

ENV = ENVIRONMENT

if __name__ == '__main__':
    print('CONFIG_PATH: {}'.format(CONFIG_PATH))
