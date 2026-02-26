import logging
from flask import Flask
from config import LOG_LEVEL, LOG_FORMAT
from db import init_db
from routes.users import users_bp

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.register_blueprint(users_bp)

if __name__ == '__main__':
    init_db()
    logger.info("Starting Flask server on http://127.0.0.1:5000")
    app.run(debug=True)
