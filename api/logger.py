# 標準ライブラリ
from logging import INFO, Formatter, Logger, StreamHandler
from logging import getLogger as _getLogger


def getLogger(name: str, level: str | int = INFO) -> Logger:
    """
    カスタムロガーを取得または作成します。

    Args:
        name (str): ロガーの名前。
        level (Union[str, int], optional): ログレベル。デフォルトは INFO。

    Returns:
        Logger: カスタム設定されたロガー。
    """
    logger = _getLogger(name)

    # ハンドラーがまだ追加されていない場合のみ設定
    if not logger.handlers:
        # 標準出力用のハンドラーを作成
        handler = StreamHandler()

        # ログレベルが無効な場合はエラー
        if not isinstance(level, str | int):
            raise ValueError(f"Invalid log level: {level}")

        # ハンドラーのレベルを設定
        handler.setLevel(level)

        # 一般的なフォーマットを設定
        formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        # ロガーにハンドラーを追加
        logger.setLevel(level)
        logger.addHandler(handler)

    return logger
