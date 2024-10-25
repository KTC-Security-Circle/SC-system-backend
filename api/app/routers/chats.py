from fastapi import APIRouter, Depends, HTTPException
from api.app.dtos.chatlog_dtos import ChatCreateDTO, ChatLogDTO, ChatSearchDTO, ChatUpdateDTO, ChatOrderBy
from api.app.models import User, ChatLog
from api.app.role import Role, role_required
from api.app.security.jwt_token import get_current_user
from api.app.database.database import add_db_record, select_table, update_record, delete_record
from api.app.database.engine import get_engine
from datetime import datetime
from typing import Optional
from sc_system_ai import main as SC_AI
from api.logger import getLogger
import logging
import asyncio
from fastapi.responses import StreamingResponse

router = APIRouter()
logger = getLogger("chatlog_router")
logger.setLevel(logging.DEBUG)


# 通常のジェネレータを非同期ジェネレータに変換するラッパー関数
async def async_wrap(generator):
    for item in generator:
        yield item
        await asyncio.sleep(0)  # イテレーション間にコンテキストの切り替えを可能にする


@router.post("/input/chat/", response_model=ChatLogDTO, tags=["chat_post"])
@role_required(Role.STUDENT)
async def create_chatlog(
    chatlog: ChatCreateDTO,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"チャット作成リクエストを受け付けました。ユーザーID: {current_user.id}")

    try:
        # ユーザー情報を設定
        user_info = User(name=current_user.name, major=current_user.major)

        # AI応答を生成するためのエージェントを作成
        agent = SC_AI.Agent(user_info=user_info, is_streaming=True)

        # AIがメッセージに対してストリーミング返信を生成
        bot_reply_generator = async_wrap(agent.invoke(message=chatlog.message))

        # ストリーミングレスポンス用のジェネレータ関数
        async def bot_reply_streamer():
            try:
                async for chunk in bot_reply_generator:
                    yield chunk
                    await asyncio.sleep(0.1)  # 少しの遅延を入れてリアルタイム感を強調
            except Exception as stream_err:
                logger.error(f"ストリーミング中にエラーが発生しました: {str(stream_err)}")
                yield "[ストリーミングエラー: 応答の一部が欠落しています]"

        # チャットログを作成
        chat_log_data = ChatLog(
            message=chatlog.message,
            bot_reply="",  # ストリーミング中のため、完全なレスポンスは後で取得
            pub_data=chatlog.pub_data or datetime.now(),
            session_id=chatlog.session_id,
        )

        # データベースにチャットログを追加
        await add_db_record(engine, chat_log_data)

        logger.info("新しいチャットログを登録しました。")
        logger.info(f"チャットID:{chat_log_data.id}")
        logger.info(f"チャット内容:{chat_log_data.message}")
        logger.info(f"投稿日時:{chat_log_data.pub_data}")
        logger.info(f"セッションID:{chat_log_data.session_id}")

        # リアルタイムでストリーミングレスポンスを返す
        return StreamingResponse(bot_reply_streamer(), media_type="text/plain")

    except Exception as e:
        logger.error(f"チャットログ作成中にエラーが発生しました: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"チャットログの作成中にエラーが発生しました。{str(e)}"
        )


@router.get("/view/chat/", response_model=list[ChatLogDTO], tags=["chat_get"])
@role_required(Role.STUDENT)
async def view_chatlog(
    search_params: ChatSearchDTO = Depends(),
    order_by: Optional[ChatOrderBy] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = 0,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"チャットログ取得リクエストを受け付けました。検索条件: {search_params}")

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
        order_by=order_by
    )

    logger.info(f"チャットログ取得完了: {len(chatlog)}件")

    chatlog_dto_list = [
        ChatLogDTO(
            id=log.id,
            message=log.message,
            bot_reply=log.bot_reply,
            pub_data=log.pub_data,
            session_id=log.session_id
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
    current_user: User = Depends(get_current_user)
):
    logger.info(f"チャットログ更新リクエストを受け付けました。チャットID: {chat_id}")

    conditions = {"id": chat_id}
    updates_dict = updates.model_dump(exclude_unset=True)
    updated_record = await update_record(engine, ChatLog, conditions, updates_dict)

    logger.info(
        f"チャットログを更新しました。チャットID: {updated_record.id}, 更新内容: {updates_dict}")

    updated_chatlog_dto = ChatLogDTO(
        id=updated_record.id,
        message=updated_record.message,
        bot_reply=updated_record.bot_reply,
        pub_data=updated_record.pub_data,
        session_id=updated_record.session_id
    )

    return updated_chatlog_dto


@router.delete("/delete/chat/{chat_id}/", response_model=dict, tags=["chat_delete"])
@role_required(Role.STUDENT)
async def delete_chatlog(
    chat_id: int,
    engine=Depends(get_engine),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"チャットログ削除リクエストを受け付けました。チャットID: {chat_id}")

    conditions = {"id": chat_id}
    result = await delete_record(engine, ChatLog, conditions)

    logger.info(f"チャットログを削除しました。チャットID: {chat_id}")

    return {"message": "チャットログが削除されました"}
