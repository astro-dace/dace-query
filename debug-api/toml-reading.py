import configparser
from pathlib import Path

config = configparser.ConfigParser()

config.read(Path('../pyprosaject.toml'))
print(list(config['tool.poetry'].keys()))
print(config['tool.poetry']['version'])
