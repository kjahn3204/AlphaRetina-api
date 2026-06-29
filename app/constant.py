import os

from rcore.constant import WORK_DIR

CONFIG_DIR = os.path.join(WORK_DIR, 'config')
BASE_CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.base.yaml')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.yaml')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
