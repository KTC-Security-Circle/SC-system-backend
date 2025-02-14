import asyncio
import json
import logging
from collections.abc import AsyncGenerator, Generator
from datetime import datetime
from typing import Annotated, Any
import traceback

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sc_system_ai import main as SC_AI
from sc_system_ai.template.session_naming import session_naming
from sqlalchemy import Engine

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
from api.app.models import ChatLog, User, Session
from api.app.security.role import Role, role_required
from api.app.security.jwt_token import get_current_user
from api.app.security.role import Role, role_required
from api.logger import getLogger

router = APIRouter()
logger = getLogger("chatlog_router")
logger.setLevel(logging.DEBUG)


# @router.post("/input/chat-demo", tags=["chat_post"])
# async def create_chatlog_demo(chatlog: ChatCreateDTO) -> StreamingResponse:
#     logger.info(
#         f"チャットデモリクエストを受け付けました。メッセージ: {chatlog.message}"
#     )

#     # テスト用ジェネレータ
#     async def bot_reply_generator():
#         demo_replies = [
#             "こんにちは！",
#             "どのようなご用件でしょうか？",
#             "今日は晴れですね！",
#             "何か他にお手伝いできることはありますか？",
#         ]
#         for i, reply in enumerate(demo_replies):
#             logger.debug(f"デモ応答 {i}: {reply}")
#             yield json.dumps({"index": i, "message": reply}) + "\n"
#             await asyncio.sleep(1)  # デモ応答を1秒ごとに送信

#     # StreamingResponseで応答を返す
#     try:
#         logger.debug("デモ用StreamingResponseの準備を開始")
#         return StreamingResponse(
#             bot_reply_generator(),  # 直接ジェネレータを渡す
#             media_type="application/json",
#         )
#     except Exception as e:
#         logger.error(f"デモStreamingResponseエラー: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail=f"ストリーミング中にエラーが発生しました: {str(e)}",
#         )


# @router.post("/test/resp-invoke", tags=["test"])
# async def test_resp_invoke_endpoint(chatlog: ChatCreateDTO) -> StreamingResponse:
#     """
#     resp.invoke と async_wrap を単独でテストするためのAPIエンドポイント
#     """
#     logger.info(f"単独テストリクエストを受け付けました。メッセージ: {chatlog.message}")

#     try:
#         # テスト用の AI チャットインスタンス
#         resp = SC_AI.Chat(
#             user_name="テストユーザー",
#             user_major="テスト専攻",
#             conversation=[
#                 ("human", "おはようございます！"),
#                 ("ai", "おはようございます！"),
#             ],
#             is_streaming=True,
#             return_length=5,
#         )

#         # 非同期ジェネレータの実装
#         async def bot_reply_generator():
#             try:
#                 async for chunk in resp.invoke(message=chatlog.message):
#                     logger.debug(f"Generator チャンク: {chunk}")
#                     yield json.dumps({"message": chunk}) + "\n\n"
#             except Exception as e:
#                 logger.error(f"Generator エラー: {str(e)}", exc_info=True)
#                 raise

#         # StreamingResponseを返す
#         return StreamingResponse(
#             bot_reply_generator(),
#             media_type="application/json",
#         )
#     except Exception as e:
#         logger.error(f"単独テストエラー: {str(e)}", exc_info=True)
#         raise HTTPException(
#             status_code=500,
#             detail=f"単独テスト中にエラーが発生しました: {str(e)}",
#         )


# テキストストリーム用の非同期ジェネレータラッパー
async def async_wrap(
    generator: Generator[str, None, None]
) -> AsyncGenerator[str, None]:
    try:
        for item in generator:
            logger.debug(f"Generator item: {item}")
            yield item
            await asyncio.sleep(0)
    except Exception as e:
        logger.error(f"async_wrapエラー: {str(e)}", exc_info=True)
        raise


# StreamingResponseでのリアルタイムレスポンス
async def text_stream(
    bot_reply_generator: AsyncGenerator[str, None],
    chatlog: ChatCreateDTO,
    engine: Engine,
    current_user: User,
) -> AsyncGenerator[str, None]:  # 戻り値をAsyncGeneratorに明示
    bot_reply = ""

    async def stream():
        try:
            logger.debug("Streaming開始")
            async for i, chunk in enumerate(bot_reply_generator):
                bot_reply += chunk
                yield json.dumps({"index": i, "message": chunk}) + "\n\n"
                logger.debug(f"Chunk received: {chunk}")
                await asyncio.sleep(0)
        except Exception as e:
            logger.error(f"Streaming中のエラー: {str(e)}", exc_info=True)
            raise

        try:
            # ストリーム終了後にチャットログを保存
            chat_log_data = ChatLog(
                message=chatlog.message,
                bot_reply=bot_reply,
                pub_data=chatlog.pub_data or datetime.now(),
                session_id=chatlog.session_id,
            )
            logger.debug("チャットログ保存を試みています")
            await asyncio.to_thread(add_db_record, engine, chat_log_data)
            logger.info(f"チャットログを保存しました: {chat_log_data}")

            # DTO形式で最終的なレスポンスを返す
            dto = ChatLogDTO(
                id=chat_log_data.id,
                message=chat_log_data.message,
                bot_reply=chat_log_data.bot_reply,
                pub_data=chat_log_data.pub_data,
                session_id=chat_log_data.session_id,
            )
            yield json.dumps(dto.model_dump()) + "\n"
        except Exception as e:
            logger.error(f"チャットログ保存中のエラー: {str(e)}", exc_info=True)
            raise

    return stream()


# @router.post("/input/chat", response_model=ChatLogDTO, tags=["chat_post"])
# @role_required(Role.STUDENT)
# async def create_chatlog(
#     chatlog: ChatCreateDTO,
#     engine: Annotated[Engine, Depends(get_engine)],
#     current_user: Annotated[User, Depends(get_current_user)],
# ) -> StreamingResponse:
#     logger.info(
#         f"チャット作成リクエストを受け付けました。ユーザーID: {current_user.id}"
#     )

#     try:
#         # セッションIDがない場合、新しいセッションを作成
#         if not chatlog.session_id:
#             new_session = Session(
#                 session_name="Default Session",
#                 pub_data=datetime.now(),
#                 user_id=current_user.id,
#             )
#             await add_db_record(engine, new_session)
#             chatlog.session_id = new_session.id
#             logger.info(
#                 f"新しいセッションを作成しました。セッションID: {chatlog.session_id}"
#             )

#         # get_tagged_conversationsを使用して過去の会話履歴を取得
#         tagged_conversations = await get_tagged_conversations(
#             chatlog.session_id, engine
#         )
#         logger.info(f"取得した会話履歴 (tagged_conversations): {tagged_conversations}")

#         # AI応答を生成するChatインスタンスを作成
#         resp = SC_AI.Chat(
#             user_name=current_user.name,
#             user_major=current_user.major,
#             conversation=tagged_conversations,
#             is_streaming=True,
#             return_length=5,
#         )

#         # メッセージに対するAI応答を生成し、非同期で取得
#         logger.debug(f"AIモデルに渡すデータ: {tagged_conversations}")
#         bot_reply_generator = async_wrap(resp.invoke(message=chatlog.message))
#         logger.debug("AIモデル呼び出しが成功しました")
#         logger.debug("text_streamが開始されました")
#         logger.debug(f"bot_reply_generatorの型: {type(bot_reply_generator)}")

#         # StreamingResponseでリアルタイムにAI応答を返却し、最後にDTOを返す
#         try:
#             logger.debug("StreamingResponseの準備を開始")
#             # text_streamの呼び出しを修正
#             stream = text_stream(bot_reply_generator, chatlog, engine, current_user)
#             return StreamingResponse(stream, media_type="application/json")
#         except Exception as e:
#             logger.error(f"StreamingResponseエラー: {str(e)}", exc_info=True)
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"ストリーミング中にエラーが発生しました: {str(e)}",
#             )

#     except Exception as e:
#         logger.error(f"チャットログ作成中にエラーが発生しました: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"チャットログの作成中にエラーが発生しました。{str(e)}",
#         ) from e


async def update_session_name(session_id: int, conversations: list, engine: Engine):
    """セッション名を生成して更新するヘルパー関数"""
    session_name = session_naming(conversations)
    conditions = {"id": session_id}
    updates = {"session_name": session_name}
    await update_record(
        engine=engine, model=Session, conditions=conditions, updates=updates
    )
    return session_name


@router.post("/input/chat", response_model=ChatLogDTO, tags=["chat_post"])
@role_required(Role.STUDENT)
async def create_chatlog(
    chatlog: ChatCreateDTO,
    engine: Annotated[Engine, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ChatLogDTO:
    logger.info(
        f"チャット作成リクエストを受け付けました。ユーザーID: {current_user.id}"
    )

    try:
        # 定数としてサンプルデータを定義
        SAMPLE_CONVERSATIONS = [
            ("human", "こんにちは!"),
            ("ai", "本日はどのようなご用件でしょうか？"),
        ]

        # セッションIDがない場合、新しいセッションを作成
        if not chatlog.session_id:
            new_session = Session(
                session_name="New Session",
                pub_data=datetime.now(),
                user_id=current_user.id,
            )
            await add_db_record(engine, new_session)
            chatlog.session_id = new_session.id
            logger.info(
                f"新しいセッションを作成しました。セッションID: {chatlog.session_id}, \
                一時的なセッション名: 'New Session'"
            )

        # セッションIDを使用して会話履歴を取得
        tagged_conversations = await get_tagged_conversations(
            chatlog.session_id, engine
        )
        logger.info(f"取得した会話履歴 (tagged_conversations): {tagged_conversations}")

        # 会話履歴が空の場合にサンプルデータを追加
        if not tagged_conversations:
            logger.warning("会話履歴が空のため、サンプルデータを追加します。")
            tagged_conversations.extend(SAMPLE_CONVERSATIONS)
            logger.info(f"サンプルデータが追加されました: {SAMPLE_CONVERSATIONS}")

        # AI応答を生成
        resp = SC_AI.Chat(
            user_name=current_user.name,
            user_major="fugafuga専攻", # current_user.major
            conversation=tagged_conversations,
        )

        logger.debug(f"AIモデルに渡すデータ: {tagged_conversations}")
        try:
            raw_response = resp.invoke(message=chatlog.message)
            logger.debug(f"AIモデルの応答 (raw): {raw_response}")

            # 応答が辞書型としてそのまま渡された場合の処理
            if isinstance(raw_response, dict) and {"output", "error", "document_id"} <= raw_response.keys():
                logger.debug(f"受信した応答が辞書型: {raw_response}")
                bot_reply = raw_response.get("output", "No output available.")
            else:
                # それ以外のケースはエラーメッセージを設定
                logger.warning(f"予期しない応答形式: {raw_response}")
                bot_reply = "Unexpected response format from AI."

            logger.debug(f"整形済みAI応答: {bot_reply}")

        except Exception as e:
            # エラーが発生した場合はエラーメッセージを設定
            bot_reply = f"An error occurred while processing the AI response: {e}"
            logger.error(f"AI応答データの処理中にエラーが発生しました: {e}")

            # エラー時でもレスポンスを返却
            return ChatLogDTO(
                id=None,
                message=chatlog.message,
                bot_reply=bot_reply,
                pub_data=chatlog.pub_data or datetime.now(),
                session_id=chatlog.session_id,
            )

        # チャットログを保存
        chat_log_data = ChatLog(
            message=chatlog.message,
            bot_reply=bot_reply,
            pub_data=chatlog.pub_data or datetime.now(),
            session_id=chatlog.session_id,
        )
        await add_db_record(engine, chat_log_data)

        logger.info(f"チャットログを保存しました: {chat_log_data}")
        logger.info(f"ドキュメントID:{raw_response['document_id']}")

        # 実際のデータを会話履歴に追加
        tagged_conversations.append(
            ("human", chatlog.message)
        )  # 新しいユーザーのメッセージ
        tagged_conversations.append(("ai", ""))  # AI応答は後で更新

        # サンプルデータを除外してセッション名を生成・更新
        filtered_conversations = [
            (role, text)
            for role, text in tagged_conversations
            if (role, text) not in SAMPLE_CONVERSATIONS
        ]
        session_name = await update_session_name(
            chatlog.session_id, filtered_conversations, engine
        )
        logger.info(f"セッション名を更新しました: {session_name}")

        # DTO形式でレスポンスを返却
        return ChatLogDTO(
            id=chat_log_data.id,
            message=chat_log_data.message,
            bot_reply=chat_log_data.bot_reply,
            pub_data=chat_log_data.pub_data,
            session_id=chat_log_data.session_id,
            document_id=raw_response["document_id"],
        )

    except Exception as e:
        logger.error(
            f"チャットログ作成中にエラーが発生しました: {str(e)}", exc_info=True
        )
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"チャットログの作成中にエラーが発生しました: {str(e)}\n" + tb,
        ) from e


async def get_tagged_conversations(session_id: int, engine: Engine) -> list[tuple[str, str]]:
    tagged_conversations = []
    try:
        condition = {"session_id": session_id}
        past_chats = await select_table(engine=engine, model=ChatLog, conditions=condition, order_by="pub_data")
        logger.info(f"取得した会話履歴: {past_chats}")
        if not past_chats:
            return []  # サンプルデータを返さない
        for chat in past_chats:
            if chat.message:
                tagged_conversations.append(("human", chat.message))
            if chat.bot_reply:
                tagged_conversations.append(("ai", chat.bot_reply))
        logger.info(f"タグ付けした会話履歴: {tagged_conversations}")
    except Exception as e:
        logger.error(f"会話履歴取得中にエラーが発生しました: {e}")
    return tagged_conversations


@router.get("/view/chat", response_model=list[ChatLogDTO], tags=["chat_get"])
@role_required(Role.STUDENT)
async def view_chatlog(
    search_params: Annotated[ChatSearchDTO, Depends()],
    engine: Annotated[Engine, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
    order_by: ChatOrderBy | None = None,
    limit: int | None = None,
    offset: int | None = 0,
) -> list[ChatLogDTO]:
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


@router.put("/update/chat/{chat_id}", response_model=ChatLogDTO, tags=["chat_put"])
@role_required(Role.STUDENT)
async def update_chatlog(
    chat_id: int,
    updates: ChatUpdateDTO,
    engine: Annotated[Engine, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ChatLogDTO:
    logger.info(f"チャットログ更新リクエストを受け付けました。チャットID: {chat_id}")

    conditions = {"id": chat_id}
    updates_dict = updates.model_dump(exclude_unset=True)
    updated_record = await update_record(engine, ChatLog, conditions, updates_dict)

    logger.info(f"チャットログを更新しました。チャットID: {updated_record.id}, 更新内容: {updates_dict}")

    updated_chatlog_dto = ChatLogDTO(
        id=updated_record.id,
        message=updated_record.message,
        bot_reply=updated_record.bot_reply,
        pub_data=updated_record.pub_data,
        session_id=updated_record.session_id,
    )

    return updated_chatlog_dto


@router.delete("/delete/chat/{chat_id}", response_model=dict, tags=["chat_delete"])
@role_required(Role.STUDENT)
async def delete_chatlog(
    chat_id: int,
    engine: Annotated[Engine, Depends(get_engine)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    logger.info(f"チャットログ削除リクエストを受け付けました。チャットID: {chat_id}")

    conditions = {"id": chat_id}
    await delete_record(engine, ChatLog, conditions)

    logger.info(f"チャットログを削除しました。チャットID: {chat_id}")

    return {"message": "チャットログが削除されました"}
