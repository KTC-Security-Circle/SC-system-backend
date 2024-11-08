import asyncio
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sc_system_ai import main as SC_AI

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
from api.app.role import Role, role_required
from api.app.security.jwt_token import get_current_user
from api.logger import getLogger

router = APIRouter()
logger = getLogger("chatlog_router")
logger.setLevel(logging.DEBUG)


# テキストストリーム用の非同期ジェネレータラッパー
async def async_wrap(generator):
    for item in generator:
        yield item
        await asyncio.sleep(0)


# StreamingResponseでのリアルタイムレスポンス
async def text_stream(bot_reply_generator, chatlog, engine, current_user):
    bot_reply = ""
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


@router.post("/input/chat/", response_model=ChatLogDTO, tags=["chat_post"])
@role_required(Role.STUDENT)
async def create_chatlog(
    chatlog: ChatCreateDTO,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user),
):
    logger.info(
        f"チャット作成リクエストを受け付けました。ユーザーID: {current_user.id}"
    )

    try:
        # `get_tagged_conversations`を使用して過去の会話履歴を取得
        tagged_conversations = await get_tagged_conversations(
            chatlog.session_id, engine
        )
        logger.info(f"取得した会話履歴 (tagged_conversations): {tagged_conversations}")

        # AI応答を生成するChatインスタンスを作成
        resp = SC_AI.Chat(
            user_name=current_user.name,
            user_major=current_user.major,
            conversation=tagged_conversations,
            is_streaming=True,
            return_length=5
        )

        # メッセージに対するAI応答を生成し、非同期で取得
        bot_reply_generator = async_wrap(resp.invoke(message=chatlog.message))

        # StreamingResponseでリアルタイムにAI応答を返却し、最後にDTOを返す
        return StreamingResponse(
            text_stream(bot_reply_generator, chatlog, engine, current_user),
            media_type="text/plain",
        )

    except Exception as e:
        logger.error(f"チャットログ作成中にエラーが発生しました: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"チャットログの作成中にエラーが発生しました。{str(e)}",
        )


async def get_tagged_conversations(session_id: int, engine) -> list[tuple[str, str]]:
    tagged_conversations = []

    try:
        condition = {"session_id":session_id}
        # select_tableを利用して、会話履歴を取得
        past_chats = await select_table(
            engine=engine,
            model=ChatLog,
            conditions=condition,
            order_by="pub_data"
        )

        logger.info(f"取得した会話履歴: {past_chats}")

        if not past_chats:
            logger.info(
                f"セッションID {session_id} に関連するチャットログが見つかりませんでした。"
            )
            return [
                ("human", "こんにちは!"),
                ("ai", "本日はどのようなご用件でしょうか？")
                ]

        # チャットログにタグを付けてリストを作成
        for chat in past_chats:
            if chat.message:
                tagged_conversations.append(("human", chat.message))
            if chat.bot_reply:
                tagged_conversations.append(("ai", chat.bot_reply))

        logger.info(f"タグ付けした会話履歴: {tagged_conversations}")

    except Exception as e:
        logger.error(f"会話履歴取得中にエラーが発生しました: {str(e)}")
        # エラー発生時も空のリストを返す
        return tagged_conversations

    return tagged_conversations


@router.get("/view/chat/", response_model=list[ChatLogDTO], tags=["chat_get"])
@role_required(Role.STUDENT)
async def view_chatlog(
    search_params: ChatSearchDTO = Depends(),
    order_by: ChatOrderBy | None = None,
    limit: int | None = None,
    offset: int | None = 0,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user),
):
    logger.info(
        f"チャットログ取得リクエストを受け付けました。検索条件: {search_params}"
    )

    conditions_dict = {}
    like_conditions = {}

    if search_params.session_id is not None:
        conditions_dict["session_id"] = search_params.session_id

    if search_params.message_like:
        like_conditions["message"] = search_params.message_like

    chatlog = await select_table(
        engine,
        ChatLog,
        conditions_dict,
        like_conditions=like_conditions,
        offset=offset,
        limit=limit,
        order_by=order_by,
    )

    logger.info(f"チャットログ取得完了: {len(chatlog)}件")

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
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"チャットログ更新リクエストを受け付けました。チャットID: {chat_id}")

    conditions = {"id": chat_id}
    updates_dict = updates.model_dump(exclude_unset=True)
    updated_record = await update_record(engine, ChatLog, conditions, updates_dict)

    logger.info(
        f"チャットログを更新しました。チャットID: {updated_record.id}, 更新内容: {updates_dict}"
    )

    updated_chatlog_dto = ChatLogDTO(
        id=updated_record.id,
        message=updated_record.message,
        bot_reply=updated_record.bot_reply,
        pub_data=updated_record.pub_data,
        session_id=updated_record.session_id,
    )

    return updated_chatlog_dto


@router.delete("/delete/chat/{chat_id}/", response_model=dict, tags=["chat_delete"])
@role_required(Role.STUDENT)
async def delete_chatlog(
    chat_id: int,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"チャットログ削除リクエストを受け付けました。チャットID: {chat_id}")

    conditions = {"id": chat_id}
    result = await delete_record(engine, ChatLog, conditions)

    logger.info(f"チャットログを削除しました。チャットID: {chat_id}")

    return {"message": "チャットログが削除されました"}
