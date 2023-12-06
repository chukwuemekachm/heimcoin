from os import environ
from dotenv import load_dotenv

load_dotenv()

HEIM_COIN_SECRET=environ.get('HEIM_COIN_SECRET')
HEIM_COIN_PRIVATE_KEY_PASS_PHRASE=environ.get('HEIM_COIN_PRIVATE_KEY_PASS_PHRASE')
FLASK_RUN_HOST=environ.get('FLASK_RUN_HOST')
FLASK_RUN_PORT=environ.get('FLASK_RUN_PORT')

FLASK_ENV=environ.get('FLASK_ENV')
FLASK_DEBUG=environ.get('FLASK_DEBUG')
FLASK_RELOAD=environ.get('FLASK_RELOAD')
FLASK_APP=environ.get('FLASK_APP')
