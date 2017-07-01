import logging
import os

_base_path = os.path.dirname(os.path.abspath(__file__))
_path = os.path.join(_base_path, '..', 'app.log')

_log_options = {
    'filename': _path,
    'filemode': 'w',
    'level': logging.DEBUG
}

logging.basicConfig(**_log_options)


def log(origin, message, *, logger='main', level='debug'):
    assert level in ('debug', 'info', 'warning', 'error', 'message')
    logger_obj = logging.getLogger(logger)
    if not isinstance(origin, str):
        origin = origin.__class__.__name__
    getattr(logger_obj, level)(f'#{origin}: {message}')
