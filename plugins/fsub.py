
import asyncio
from Script import script 
from pyrogram import filters, Client, enums
from pyrogram.types import ChatJoinRequest
from pyrogram.handlers import ChatJoinRequestHandler
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from database.join_reqs import req_db
from database.users_chats_db import db
from info import ADMINS
from utils import temp
from logging import getLogger

logger = getLogger(__name__)


@Client.on_chat_join_request()
async def join_reqs(client, m: ChatJoinRequest):
    if m.chat.id == temp.AUTH_CHANNEL:
        if temp.REQ_SUB:
            id = m.from_user.id
            await req_db.add_user(id=id)


@Client.on_message(filters.command("total_req") & filters.private & filters.user(ADMINS))                
async def total_requests(client, message):
    if temp.REQ_SUB:
        total = await req_db.get_all_users_count()
        await message.reply_text(f"Total Requests: {total}")
    else:
        await message.reply('Req Sub Is Off')

@Client.on_message(filters.command("del_req") & filters.private & filters.user(ADMINS))
async def purge_requests(client, message):
    if temp.REQ_SUB:
        await req_db.delete_all_users()
        await message.reply_text("Done ✅️")
    else:
        await message.reply('Req Sub Is Off')        



async def ForceSub(bot: Client, event: Message, file_id: str = False, mode="checksub"):
    is_cb = False
    if not hasattr(event, "chat"):
        event.message.from_user = event.from_user
        event = event.message
        is_cb = True

    try:
        if temp.INVITE_LINK == None:
            if_req = True if temp.REQ_SUB else False 
            link = (await bot.create_chat_invite_link(chat_id=int(temp.AUTH_CHANNEL), creates_join_request=if_req)).invite_link
            temp.INVITE_LINK = link
            print("Created Invite Link !")
        else:
            link = temp.INVITE_LINK
            
    except Exception as e:
        print(f"Unable to create Invite link !\n\nError: {e}")
        return False
    
        
    # Mian Logic
    if temp.REQ_SUB:
        try:
            # Check if User is Requested to Join Channel
            user = await req_db.get_user(event.from_user.id)
            if user and user["id"] == event.from_user.id:
                return True
        except Exception as e:
            logger.exception(e, exc_info=True)
            await event.reply(text="Something went Wrong.")
            return False

    try:
        user = await bot.get_chat_member(chat_id=int(temp.AUTH_CHANNEL), user_id=event.from_user.id)
        if user: return True
    except UserNotParticipant:
        buttons = [[            
            InlineKeyboardButton("📢 Rᴇǫᴜᴇsᴛ Tᴏ Jᴏɪɴ", url=link)
            ],[           
            InlineKeyboardButton("🔄 Tʀʏ Aɢᴀɪɴ", callback_data=f"{mode}#{file_id}")
        ]]               
        if file_id is False: buttons.pop()
        if not is_cb:
            await event.reply(text=script.FSUB_TXT, quote=True, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.MARKDOWN)
        return False

    except FloodWait as e:
        await asyncio.sleep(e.value)
        fix_ = await ForceSub(bot, event, file_id)
        return fix_

    except Exception as err:
        print(f"Something Went Wrong! Unable to do Force Subscribe.\nError: {err}")
        await event.reply(text="Something went Wrong.")
        return False


