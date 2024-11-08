from logging import INFO, Formatter, StreamHandler
from logging import getLogger as _getLogger


def getLogger(name, level: str | int = INFO):
    logger = _getLogger(name)
    if not logger.handlers:
        # 標準出力用のハンドラーを作成
        handler = StreamHandler()
        handler.setLevel(level)

        # 一般的なフォーマットを設定
        formatter = Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        # ロガーにハンドラーを追加
        logger.setLevel(level)
        logger.addHandler(handler)
    return logger
