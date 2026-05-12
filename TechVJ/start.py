# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Modified & Fixed By Lakki

import os
import asyncio
import pyrogram

from urllib.parse import urlparse, parse_qs

from pyrogram import Client, filters, enums
from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    InputUserDeactivated,
    UserAlreadyParticipant,
    InviteHashExpired,
    UsernameNotOccupied
)

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message
)

from config import API_ID, API_HASH, ERROR_MESSAGE
from database.db import db
from TechVJ.strings import HELP_TXT


class batch_temp(object):
    IS_BATCH = {}


# =========================
# DOWNLOAD STATUS
# =========================
async def downstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(1)

    while os.path.exists(statusfile):
        try:
            with open(statusfile, "r") as f:
                txt = f.read()

            await client.edit_message_text(
                chat,
                message.id,
                f"📥 **Downloaded :** `{txt}`"
            )

            await asyncio.sleep(5)

        except:
            await asyncio.sleep(2)


# =========================
# UPLOAD STATUS
# =========================
async def upstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(1)

    while os.path.exists(statusfile):
        try:
            with open(statusfile, "r") as f:
                txt = f.read()

            await client.edit_message_text(
                chat,
                message.id,
                f"📤 **Uploaded :** `{txt}`"
            )

            await asyncio.sleep(5)

        except:
            await asyncio.sleep(2)


# =========================
# PROGRESS FUNCTION
# =========================
def progress(current, total, message, typ):
    percentage = current * 100 / total

    with open(f"{message.id}_{typ}.txt", "w") as f:
        f.write(f"{percentage:.1f}%")


# =========================
# START COMMAND
# =========================
@Client.on_message(filters.command("start"))
async def send_start(client: Client, message: Message):

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(
            message.from_user.id,
            message.from_user.first_name
        )

    buttons = [
        [
            InlineKeyboardButton(
                "❣️ Developer",
                url="https://t.me/lakki_reddy4"
            )
        ],
        [
            InlineKeyboardButton(
                "🔍 Support Group",
                url="https://t.me/lakki_redsy3"
            ),
            InlineKeyboardButton(
                "🤖 Update Channel",
                url="https://t.me/lakki_reddy3"
            )
        ]
    ]

    await message.reply_text(
        text=(
            f"<b>👋 Hi {message.from_user.mention},\n\n"
            "I am Save Restricted Content Bot.\n"
            "I can send restricted content using post links.\n\n"
            "🔐 Use /login first.\n"
            "📚 Use /help for usage guide.</b>"
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# =========================
# HELP COMMAND
# =========================
@Client.on_message(filters.command("help"))
async def send_help(client: Client, message: Message):
    await message.reply_text(HELP_TXT)


# =========================
# CANCEL COMMAND
# =========================
@Client.on_message(filters.command("cancel"))
async def send_cancel(client: Client, message: Message):

    batch_temp.IS_BATCH[message.from_user.id] = True

    await message.reply_text(
        "✅ Batch Successfully Cancelled."
    )


# =========================
# AUTO SAVE PM MEDIA
# =========================
@Client.on_message(
    filters.private
    & ~filters.bot
    & ~filters.command([
        "start",
        "help",
        "login",
        "logout",
        "cancel"
    ])
)
async def auto_save_pm(client: Client, message: Message):

    try:

        # ignore own messages
        if message.from_user and message.from_user.is_self:
            return

        # ignore text only
        if not message.media:
            return

        # save media
        await message.copy("me")

    except Exception as e:
        if ERROR_MESSAGE:
            print(f"AUTO SAVE ERROR : {e}")


# =========================
# MAIN SAVE HANDLER
# =========================
@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):

    if "https://t.me/" not in message.text and "tg://openmessage?" not in message.text:
        return

    user_id = message.from_user.id

    if batch_temp.IS_BATCH.get(user_id) is False:
        return await message.reply_text(
            "**One task already running.\nUse /cancel to stop it.**"
        )

    batch_temp.IS_BATCH[user_id] = False

    try:

        user_data = await db.get_session(user_id)

        if user_data is None:
            batch_temp.IS_BATCH[user_id] = True

            return await message.reply_text(
                "**You need to /login first.**"
            )

        acc = Client(
            "save_restricted",
            session_string=user_data,
            api_id=API_ID,
            api_hash=API_HASH
        )

        await acc.connect()

    except Exception as e:

        batch_temp.IS_BATCH[user_id] = True

        return await message.reply_text(
            f"❌ Session Expired.\n/login again.\n\n{e}"
        )

    try:

        # =========================
        # TG OPENMESSAGE LINK
        # =========================
        if "tg://openmessage?" in message.text:

            parsed = urlparse(message.text)
            params = parse_qs(parsed.query)

            chatid = int(params.get("user_id", [0])[0])
            msgid = int(params.get("message_id", [0])[0])

            await handle_private(
                client,
                acc,
                message,
                chatid,
                msgid
            )

            batch_temp.IS_BATCH[user_id] = True
            return

        datas = message.text.split("/")

        temp = datas[-1].replace("?single", "").split("-")

        fromID = int(temp[0])

        try:
            toID = int(temp[1])
        except:
            toID = fromID

        for msgid in range(fromID, toID + 1):

            if batch_temp.IS_BATCH.get(user_id):
                break

            # =========================
            # PRIVATE LINK
            # =========================
            if "https://t.me/c/" in message.text:

                chatid = int("-100" + datas[4])

                try:
                    await handle_private(
                        client,
                        acc,
                        message,
                        chatid,
                        msgid
                    )

                except Exception as e:
                    if ERROR_MESSAGE:
                        await message.reply_text(f"Error : {e}")

            # =========================
            # BOT LINK
            # =========================
            elif "https://t.me/b/" in message.text:

                username = datas[4]

                try:
                    await handle_private(
                        client,
                        acc,
                        message,
                        username,
                        msgid
                    )

                except Exception as e:
                    if ERROR_MESSAGE:
                        await message.reply_text(f"Error : {e}")

            # =========================
            # PUBLIC LINK
            # =========================
            else:

                username = datas[3]

                try:

                    msg = await client.get_messages(
                        username,
                        msgid
                    )

                    await client.copy_message(
                        message.chat.id,
                        msg.chat.id,
                        msg.id,
                        reply_to_message_id=message.id
                    )

                except UsernameNotOccupied:

                    await message.reply_text(
                        "❌ Username not occupied."
                    )

                except Exception:

                    try:
                        await handle_private(
                            client,
                            acc,
                            message,
                            username,
                            msgid
                        )

                    except Exception as e:
                        if ERROR_MESSAGE:
                            await message.reply_text(f"Error : {e}")

            await asyncio.sleep(2)

    finally:

        batch_temp.IS_BATCH[user_id] = True

        try:
            await acc.disconnect()
        except:
            pass


# =========================
# HANDLE PRIVATE
# =========================
async def handle_private(
    client: Client,
    acc,
    message: Message,
    chatid,
    msgid
):

    msg: Message = await acc.get_messages(chatid, msgid)

    if msg.empty:
        return

    msg_type = get_message_type(msg)

    if not msg_type:
        return

    chat = message.chat.id

    # =========================
    # TEXT
    # =========================
    if msg_type == "Text":

        try:

            await client.send_message(
                chat_id=chat,
                text=msg.text,
                entities=msg.entities,
                reply_to_message_id=message.id
            )

        except Exception as e:

            if ERROR_MESSAGE:
                await message.reply_text(f"Error : {e}")

        return

    # =========================
    # STATUS MESSAGE
    # =========================
    smsg = await message.reply_text("📥 Downloading...")

    down_file = f"{message.id}_down.txt"
    up_file = f"{message.id}_up.txt"

    asyncio.create_task(
        downstatus(client, down_file, smsg, chat)
    )

    # =========================
    # DOWNLOAD MEDIA
    # =========================
    try:

        file = await acc.download_media(
            msg,
            progress=progress,
            progress_args=[message, "down"]
        )

        if os.path.exists(down_file):
            os.remove(down_file)

    except Exception as e:

        if ERROR_MESSAGE:
            await message.reply_text(f"Download Error : {e}")

        return await smsg.delete()

    asyncio.create_task(
        upstatus(client, up_file, smsg, chat)
    )

    caption = msg.caption if msg.caption else None

    # =========================
    # DOCUMENT
    # =========================
    if msg_type == "Document":

        thumb = None

        try:
            thumb = await acc.download_media(
                msg.document.thumbs[0].file_id
            )
        except:
            pass

        await client.send_document(
            chat,
            document=file,
            thumb=thumb,
            caption=caption,
            reply_to_message_id=message.id,
            progress=progress,
            progress_args=[message, "up"]
        )

        if thumb and os.path.exists(thumb):
            os.remove(thumb)

    # =========================
    # VIDEO
    # =========================
    elif msg_type == "Video":

        thumb = None

        try:
            thumb = await acc.download_media(
                msg.video.thumbs[0].file_id
            )
        except:
            pass

        await client.send_video(
            chat,
            video=file,
            duration=msg.video.duration,
            width=msg.video.width,
            height=msg.video.height,
            thumb=thumb,
            caption=caption,
            reply_to_message_id=message.id,
            progress=progress,
            progress_args=[message, "up"]
        )

        if thumb and os.path.exists(thumb):
            os.remove(thumb)

    # =========================
    # PHOTO
    # =========================
    elif msg_type == "Photo":

        await client.send_photo(
            chat,
            photo=file,
            caption=caption,
            reply_to_message_id=message.id
        )

    # =========================
    # AUDIO
    # =========================
    elif msg_type == "Audio":

        thumb = None

        try:
            thumb = await acc.download_media(
                msg.audio.thumbs[0].file_id
            )
        except:
            pass

        await client.send_audio(
            chat,
            audio=file,
            thumb=thumb,
            caption=caption,
            reply_to_message_id=message.id,
            progress=progress,
            progress_args=[message, "up"]
        )

        if thumb and os.path.exists(thumb):
            os.remove(thumb)

    # =========================
    # VOICE
    # =========================
    elif msg_type == "Voice":

        await client.send_voice(
            chat,
            voice=file,
            caption=caption,
            reply_to_message_id=message.id,
            progress=progress,
            progress_args=[message, "up"]
        )

    # =========================
    # STICKER
    # =========================
    elif msg_type == "Sticker":

        await client.send_sticker(
            chat,
            sticker=file,
            reply_to_message_id=message.id
        )

    # =========================
    # ANIMATION
    # =========================
    elif msg_type == "Animation":

        await client.send_animation(
            chat,
            animation=file,
            caption=caption,
            reply_to_message_id=message.id
        )

    # =========================
    # CLEANUP
    # =========================
    try:

        if os.path.exists(up_file):
            os.remove(up_file)

        if os.path.exists(file):
            os.remove(file)

    except:
        pass

    try:
        await smsg.delete()
    except:
        pass


# =========================
# GET MESSAGE TYPE
# =========================
def get_message_type(
    msg: pyrogram.types.messages_and_media.message.Message
):

    if msg.document:
        return "Document"

    elif msg.video:
        return "Video"

    elif msg.animation:
        return "Animation"

    elif msg.sticker:
        return "Sticker"

    elif msg.voice:
        return "Voice"

    elif msg.audio:
        return "Audio"

    elif msg.photo:
        return "Photo"

    elif msg.text:
        return "Text"

    return None            except:
                batch_temp.IS_BATCH[message.from_user.id] = True
                return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
            
            # private
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try:
                    await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)



            if "tg://openmessage?" in message.text:
              try:
                  from urllib.parse import urlparse, parse_qs

                  parsed = urlparse(message.text)
                  params = parse_qs(parsed.query)

                  user_id = int(params.get("user_id", [0])[0])
                  msgid = int(params.get("message_id", [0])[0])

        # chatid = user_id  ✅ direct ga numeric ID use cheyyali
                  chatid = user_id

        # ikada forward/copy cheseydaniki
                  try:
                      await client.forward_messages(
                          chat_id=message.chat.id,   # where to send
                          from_chat_id=chatid,       # from this user
                          message_ids=msgid
                      )
                  except Exception as e:
                      await client.send_message(
                          message.chat.id,
                          f"Error forwarding message: {e}",
                          reply_to_message_id=message.id
                      )

              except Exception as e:
                  if ERROR_MESSAGE:
                      await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            
            # public
            else:
                username = datas[3]

                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    return
                try:
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    try:    
                        await handle_private(client, acc, message, username, msgid)               
                    except Exception as e:
                        if ERROR_MESSAGE == True:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # wait time
            await asyncio.sleep(3)
        batch_temp.IS_BATCH[message.from_user.id] = True


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 
    chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        return await smsg.delete()
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
            
    if "Document" == msg_type:
        try:
            ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)
        

    elif "Video" == msg_type:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)     

    elif "Voice" == msg_type:
        try:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        try:
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None

        try:
            await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
        if ph_path != None: os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)
    await client.delete_messages(message.chat.id,[smsg.id])


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass
        
