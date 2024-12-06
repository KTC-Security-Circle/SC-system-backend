import asyncio
import logging
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sc_system_ai import main as SC_AI
from sqlmodel import Session

from api.app.database.database import (
    add_db_record,
    delete_record,
    select_table,
    update_record,
)
from api.app.database.engine import get_engine
from api.app.dtos.chatlog_dtos import (
    ChatCreateDTO,
    ChatLogDTO,
    ChatOrderBy,
    ChatSearchDTO,
    ChatUpdateDTO,
)
from api.app.models import ChatLog, User
from api.app.security.jwt_token import get_current_user
from api.app.security.role import Role, role_required
from api.logger import getLogger

router = APIRouter()
logger = getLogger("chatlog_router", logging.DEBUG)


# テキストストリーム用の非同期ジェネレータラッパー
async def async_wrap(generator: Any) -> AsyncGenerator[str, None]:
    """
    非同期ジェネレータラッパー。

    Args:
        generator (Any): 同期ジェネレータ。

    Yields:
        str: ジェネレータの各要素。
    """
    for item in generator:
        yield item
        await asyncio.sleep(0)


# StreamingResponseでのリアルタイムレスポンス
async def text_stream(
    bot_reply_generator: AsyncGenerator[str, None],
    chatlog: ChatCreateDTO,
    engine: Session,
    current_user: User,
) -> AsyncGenerator[str, None]:
    """
    StreamingResponse用のリアルタイムレスポンス。

    Args:
        bot_reply_generator (AsyncGenerator[str, None]): AI応答の非同期ジェネレータ。
        chatlog (ChatCreateDTO): ユーザーからのチャットログデータ。
        engine (Session): データベースセッション。
        current_user (User): 現在の認証済みユーザー。

    Yields:
        str: ストリームレスポンスとして送信するデータ。
    """
    bot_reply = ""

    try:
        # 非同期ジェネレータから応答を取得
        async for chunk in bot_reply_generator:
            bot_reply += chunk
            yield chunk  # 各チャンクをリアルタイムに返す

        # ストリームが終了したら、チャットログをデータベースに保存
        chat_log_data = ChatLog(
            message=chatlog.message,
            bot_reply=bot_reply,
            pub_data=chatlog.pub_data or datetime.now(),
            session_id=chatlog.session_id,
        )
        await add_db_record(engine, chat_log_data)

        # 最後にDTOをJSON形式で返す
        dto = ChatLogDTO(
            id=chat_log_data.id,
            message=chat_log_data.message,
            bot_reply=chat_log_data.bot_reply,
            pub_data=chat_log_data.pub_data,
            session_id=chat_log_data.session_id,
        )
        yield f"\n\n{dto.model_dump_json()}"  # DTOをJSONとして出力

    except Exception as e:
        logger.error(f"テキストストリーム中にエラーが発生しました: {e}")
        raise


@router.post("/input/chat/", response_model=ChatLogDTO, tags=["chat_post"])
@role_required(Role.STUDENT)
async def create_chatlog(
    chatlog: ChatCreateDTO,
    engine: Annotated[Session, Depends(get_engine)],  # データベースセッションの依存関係を明示
    current_user: Annotated[User, Depends(get_current_user)],
) -> StreamingResponse:
    """
    新しいチャットログを作成し、AIの応答をストリーミングで返却。

    Args:
        chatlog (ChatCreateDTO): チャットの作成データ。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        StreamingResponse: AI応答をリアルタイムにストリーミング。
    """
    logger.info(f"チャット作成リクエストを受け付けました。ユーザーID: {current_user.id}")

    try:
        # セッションIDがNoneの場合は例外をスロー
        if chatlog.session_id is None:
            raise HTTPException(
                status_code=400,
                detail="セッションIDが指定されていません。",
            )

        # 過去の会話履歴を取得
        tagged_conversations = await get_tagged_conversations(chatlog.session_id, engine)
        logger.debug(f"取得した会話履歴: {tagged_conversations}")

        # AI応答を生成
        resp = SC_AI.Chat(
            user_name=current_user.name,
            user_major=current_user.major,
            conversation=tagged_conversations,
            is_streaming=True,
            return_length=5,
        )
        bot_reply_generator = async_wrap(resp.invoke(message=chatlog.message))

        # StreamingResponseを返す
        return StreamingResponse(
            text_stream(bot_reply_generator, chatlog, engine, current_user),
            media_type="text/plain",
        )

    except Exception as e:
        logger.error(f"チャットログ作成中にエラーが発生しました: {e}")
        raise HTTPException(
            status_code=500,
            detail="チャットログの作成中にエラーが発生しました。",
        )


async def get_tagged_conversations(session_id: int, engine: Session) -> list[tuple[str, str]]:
    """
    過去の会話履歴を取得し、タグを付けてリスト形式で返す。

    Args:
        session_id (int): 対象のセッションID。
        engine (Session): データベースセッション。

    Returns:
        List[Tuple[str, str]]: タグ付けされた会話履歴。
    """
    tagged_conversations: list[tuple[str, str]] = []

    try:
        # 条件を設定
        condition = {"session_id": session_id}

        # 過去の会話履歴を取得
        past_chats = await select_table(
            engine=engine,
            model=ChatLog,
            conditions=condition,
            order_by="pub_data",
        )

        logger.info(f"取得した会話履歴: {past_chats}")

        if not past_chats:
            logger.info(f"セッションID {session_id} に関連するチャットログが見つかりませんでした。")
            return [
                ("human", "こんにちは!"),
                ("ai", "本日はどのようなご用件でしょうか？"),
            ]

        # チャットログにタグを付けてリストを作成
        tagged_conversations = [("human", chat.message) for chat in past_chats if chat.message] + [
            ("ai", chat.bot_reply) for chat in past_chats if chat.bot_reply
        ]

        logger.info(f"タグ付けした会話履歴: {tagged_conversations}")

    except Exception as e:
        logger.error(f"会話履歴取得中にエラーが発生しました: {str(e)}")
        # エラー発生時も空のリストを返す
        return []

    return tagged_conversations


@router.get("/view/chat/", response_model=list[ChatLogDTO], tags=["chat_get"])
@role_required(Role.STUDENT)
async def view_chatlog(
    engine: Annotated[Session, Depends(get_engine)],  # デフォルト値なし
    current_user: Annotated[User, Depends(get_current_user)],  # デフォルト値なし
    search_params: Annotated[ChatSearchDTO, Depends()],  # デフォルト値なし
    order_by: ChatOrderBy | None = None,  # デフォルト値あり
    limit: Annotated[int | None, Query(ge=1)] = None,  # デフォルト値あり
    offset: Annotated[int, Query(ge=0)] = 0,  # デフォルト値あり
) -> list[ChatLogDTO]:
    """
    チャットログを取得するエンドポイント。

    Args:
        search_params (ChatSearchDTO): 検索条件。
        order_by (ChatOrderBy | None): 並び順の指定。
        limit (int | None): 最大取得件数。
        offset (int): スキップする件数。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        list[ChatLogDTO]: チャットログのDTOリスト。
    """
    logger.info(f"チャットログ取得リクエストを受け付けました。検索条件: {search_params}")

    # 検索条件を構築
    conditions_dict = {}
    like_conditions = {}

    if search_params.session_id is not None:
        conditions_dict["session_id"] = search_params.session_id

    if search_params.message_like:
        like_conditions["message"] = search_params.message_like

    # チャットログをデータベースから取得
    try:
        chatlog = await select_table(
            engine=engine,
            model=ChatLog,
            conditions=conditions_dict,
            like_conditions=like_conditions,
            offset=offset,
            limit=limit,
            order_by=order_by,
        )
        logger.info(f"チャットログ取得完了: {len(chatlog)}件")
    except Exception as e:
        logger.error(f"チャットログの取得中にエラーが発生しました: {e}")
        raise HTTPException(
            status_code=500,
            detail="チャットログの取得中にエラーが発生しました。",
        )

    # DTOリストを作成
    chatlog_dto_list = [
        ChatLogDTO(
            id=log.id,
            message=log.message,
            bot_reply=log.bot_reply,
            pub_data=log.pub_data,
            session_id=log.session_id,
        )
        for log in chatlog
    ]

    return chatlog_dto_list


@router.put("/update/chat/{chat_id}/", response_model=ChatLogDTO, tags=["chat_put"])
@role_required(Role.STUDENT)
async def update_chatlog(
    chat_id: int,
    updates: ChatUpdateDTO,
    engine: Annotated[Session, Depends(get_engine)],  # Annotatedを使用
    current_user: Annotated[User, Depends(get_current_user)],  # Annotatedを使用
) -> ChatLogDTO:
    """
    チャットログを更新するエンドポイント。

    Args:
        chat_id (int): 更新対象のチャットID。
        updates (ChatUpdateDTO): 更新内容。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        ChatLogDTO: 更新後のチャットログ。
    """
    logger.info(f"チャットログ更新リクエストを受け付けました。チャットID: {chat_id}")

    conditions = {"id": chat_id}
    updates_dict = updates.model_dump(exclude_unset=True)
    updated_record = await update_record(engine, ChatLog, conditions, updates_dict)

    logger.info(f"チャットログを更新しました。チャットID: {updated_record.id}, 更新内容: {updates_dict}")

    return ChatLogDTO(
        id=updated_record.id,
        message=updated_record.message,
        bot_reply=updated_record.bot_reply,
        pub_data=updated_record.pub_data,
        session_id=updated_record.session_id,
    )


@router.delete("/delete/chat/{chat_id}/", response_model=dict, tags=["chat_delete"])
@role_required(Role.STUDENT)
async def delete_chatlog(
    chat_id: int,
    engine: Annotated[Session, Depends(get_engine)],  # Annotatedを使用
    current_user: Annotated[User, Depends(get_current_user)],  # Annotatedを使用
) -> dict[str, str]:
    """
    チャットログを削除するエンドポイント。

    Args:
        chat_id (int): 削除対象のチャットID。
        engine (Session): データベースセッション。
        current_user (User): 現在認証されているユーザー。

    Returns:
        dict[str, str]: 削除完了メッセージ。
    """
    logger.info(f"チャットログ削除リクエストを受け付けました。チャットID: {chat_id}")

    conditions = {"id": chat_id}
    await delete_record(engine, ChatLog, conditions)

    logger.info(f"チャットログを削除しました。チャットID: {chat_id}")

    return {"message": "チャットログが削除されました"}
