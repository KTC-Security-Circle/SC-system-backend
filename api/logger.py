from logging import getLogger as _getLogger, StreamHandler, INFO


def getLogger(name, level: str | int = INFO):
    logger = _getLogger(name)
    handler = StreamHandler()
    handler.setLevel(level)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
