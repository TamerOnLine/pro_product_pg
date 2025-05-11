# config/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_file = os.path.join('logs', 'error.log')
    file_handler = RotatingFileHandler(log_file, maxBytes=102400, backupCount=5)
    file_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)

    if not app.logger.handlers:
        app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.ERROR)
