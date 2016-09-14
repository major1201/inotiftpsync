# encoding=utf-8
from __future__ import division, absolute_import, with_statement, print_function

_logger = None


def initialize():
    import os
    import sys
    import logging
    import logging.handlers
    from utils import setting, num, strings

    global _logger

    conf = setting.conf.get("system")

    _fmt = '[%(asctime)s %(levelname)s] %(message)s'
    _formatter = logging.Formatter(_fmt)
    _logger = logging.getLogger()
    _log_level = num.safe_int(conf.get("log_level"), logging.NOTSET)

    # stream logger
    if num.safe_int(conf.get("log_stdout")) == 1:
        _stream_handler = logging.StreamHandler(sys.stdout)
        _stream_handler.setFormatter(_formatter)
        _stream_handler.setLevel(_log_level)
        _logger.addHandler(_stream_handler)

    # file logger
    if num.safe_int(conf.get("log_file")) == 1:
        if strings.is_blank(conf.get("log_file_path")):
            path = os.path.join(os.path.dirname(__file__), "..", conf.get("project_name") + ".log")
        else:
            path = conf.get("log_file_path")
        _file_handler = logging.handlers.TimedRotatingFileHandler(path, when='d', backupCount=5, encoding="utf-8")
        _file_handler.setFormatter(_formatter)
        _file_handler.setLevel(_log_level)
        _logger.addHandler(_file_handler)

    _logger.setLevel(_log_level)


def critical(msg):
    _logger.critical(msg)


def error(msg):
    _logger.error(msg)


def warning(msg):
    _logger.warning(msg)


def info(msg):
    _logger.info(msg)


def debug(msg):
    _logger.debug(msg)


def error_traceback():
    import traceback
    format_exc = traceback.format_exc()
    error(format_exc)
    return format_exc
