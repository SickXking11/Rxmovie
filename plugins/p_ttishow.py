from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from info import ADMINS, LOG_CHANNEL, CHANNEL_LINK, GROUP_LINK
from database.users_chats_db import db
from database.ia_filterdb import Media, db as fdb
from utils import get_size, temp, get_settings
from Script import script
from pyrogram.errors import ChatAdminRequired, FloodWait 
import os, sys, asyncio


@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    r_j_check = [u.id for u in message.new_chat_members]
    if temp.ME in r_j_check:
        if not await db.get_chat(message.chat.id):                        
            total=await client.get_chat_members_count(message.chat.id)
            r_j = message.from_user.mention if message.from_user else "Anonymous" 
            try:
                await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(n=message.chat.title, id=message.chat.id, tot=total, u=message.chat.username, r=r_j))
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(n=message.chat.title, id=message.chat.id, tot=total, u=message.chat.username, r=r_j))       
            await db.add_chat(message.chat.id, message.chat.title)
        
        if message.chat.id in temp.BANNED_CHATS:
            # Inspired from a boat of a banana tree
            reply_markup=InlineKeyboardMarkup(buttons)
            k = await message.reply(
                text='<b>CHAT NOT ALLOWED 🐞\n\nMy admins has restricted me from working here ! If you want to know more about it contact support..</b>',
            )
            try:
                await k.pin()
            except:
                pass
            await bot.leave_chat(message.chat.id)
            return
        button = InlineKeyboardMarkup([[
            InlineKeyboardButton('ʜᴇʟᴩ', url=f'http://t.me/{temp.U_NAME}?start=help')
            ]])
        await message.reply_text(
            text=f"<b>Thankyou For Adding Me In {message.chat.title} ❣️\n\nIf You Have Any Questions & Doubts About Using Me? Click  Help</b>",
            reply_markup=button)
    else:
        settings = await get_settings(message.chat.id)
        if settings["welcome"]:
            for u in message.new_chat_members:
                if (temp.MELCOW).get('welcome') is not None:
                    try:
                        await (temp.MELCOW['welcome']).delete()
                    except:
                        pass
                
                temp.MELCOW['welcome'] = await message.reply(
                    text=f"<b>Hey , {u.mention}, Welcome To  <a href=https://t.me/{message.chat.username}>{message.chat.title}</a>\nPlease Request Your Movie To Bot Is Give Your Movie 🤩</b>\n\nNB : <code>Don'a Ask Camera Prints Here</code>",                  
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton('🎬 ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ', url=CHANNEL_LINK)
                        ],[
                        InlineKeyboardButton('📽️ ᴍᴏᴠɪᴇ ɢʀᴏᴜᴩ', url=GROUP_LINK)
                        ]]
                    )
                )
        


@Client.on_message(filters.command('id'))
async def showid(client, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        user_id = message.chat.id
        first = message.from_user.first_name
        last = message.from_user.last_name or ""
        username = message.from_user.username
        dc_id = message.from_user.dc_id or ""
        await message.reply_text(f"<b>➲ First Name:</b> {first}\n<b>➲ Last Name:</b> {last}\n<b>➲ Username:</b> {username}\n<b>➲ Telegram ID:</b> <code>{user_id}</code>\n<b>➲ Data Centre:</b> <code>{dc_id}</code>")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        id = message.chat.id
        un = message.chat.username
        tt = message.chat.title 
        await message.reply_text(f"➲ Title: {tt}\n\n➲ Chat ID: <code>{id}</code>\n➲ ChatUN: @{un}")
        
@Client.on_message(filters.command('stats') & filters.private)
async def stasus_check(client, message):
        total = await Media.count_documents()
        fmonsize = (await fdb.command("dbstats"))['dataSize']
        ffree = 536870912 - fmonsize
        fmonsize = get_size(fmonsize)
        ffree = get_size(ffree)
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        sts = await message.reply("ᴡᴀɪᴛ.....")
        await sts.edit_text(
            text=script.STATUS_TXT.format(
                users=users,
                chats=chats,
                used=monsize,
                free=free,
                total=total,
                fused=fmonsize,
                ffree=ffree),
            parse_mode=enums.ParseMode.HTML
        )

@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        await bot.send_message(
            chat_id=chat,
            text='<b>Hello Friends, \nMy admin has told me to leave from group so i go! If you wanna add me again contact my support group.</b>',
        )

        await bot.leave_chat(chat)
        await message.reply(f"left the chat `{chat}`")
    except Exception as e:
        await message.reply(f'Error - {e}')

@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply("Chat Not Found In DB")
    if cha_t['is_disabled']:
        return await message.reply(f"This chat is already disabled:\nReason-<code> {cha_t['reason']} </code>")
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply('Chat Successfully Disabled')
    try:
        await bot.send_message(
            chat_id=chat_, 
            text=f'<b>Hello Friends, \nMy admin has told me to leave from group so i go! If you wanna add me again contact my support group.</b> \nReason : <code>{reason}</code>',
        )
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("Chat Not Found In DB !")
    if not sts.get('is_disabled'):
        return await message.reply('This chat is not yet disabled.')
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    await message.reply("Chat Successfully re-enabled")


@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    try:
        link = await bot.create_chat_invite_link(chat)
    except ChatAdminRequired:
        return await message.reply("Invite Link Generation Failed, Iam Not Having Sufficient Rights")
    except Exception as e:
        return await message.reply(f'Error {e}')
    await message.reply(f'Here is your Invite Link {link.invite_link}')

@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    # https://t.me/GetTGLink/4185
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply("This might be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(f"{k.mention} is already banned\nReason: {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply(f"Successfully banned {k.mention}")


    
@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply("Thismight be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(f"{k.mention} is not yet banned.")
        await db.remove_ban(k.id)
        temp.BANNED_USERS.remove(k.id)
        await message.reply(f"Successfully unbanned {k.mention}")


    
@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    # https://t.me/GetTGLink/4184
    raju = await message.reply('Getting List Of Users')
    users = await db.get_all_users()
    out = "Users Saved In DB Are:\n\n"
    async for user in users:
        out += f"<a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += '( Banned User )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="List Of Users")

@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    raju = await message.reply('Getting List Of chats')
    chats = await db.get_all_chats()
    out = "Chats Saved In DB Are:\n\n"
    async for chat in chats:
        out += f"**Title:** `{chat['title']}`\n**- ID:** `{chat['id']}`"
        if chat['chat_status']['is_disabled']:
            out += '( Disabled Chat )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="List Of Chats")




@Client.on_message(filters.command("set_sub") & filters.user(ADMINS))
async def set_sub(b, m):
    await db.add_key()
    if len(m.command) == 1:
        return await m.reply("Send Command With Force Sub Channel Id Like /set_sub -100123456789")
    raw_id = m.text.split(" ", 1)[1]
    try:
        chat = await b.get_chat(int(raw_id))
    except ChatAdminRequired:
        return await m.reply("Channel Parameter Invalid. Iam Not Having Full Admin Rights In Your Channel. Please Add Admin With Full Admin Permeation")
    except PeerIdInvalid:
        return await m.reply("Bot Is Not Added In This Channel. Please Add With Full Admin Permeation")
    except Exception as e:
        return await m.reply(f'Error {e}')
   
    try:
        link = (await b.create_chat_invite_link(int(chat.id))).invite_link
    except Exception as e:
        print(e)
        link = "None"
    await db.set_channel(chat.id)
    temp.AUTH_CHANNEL = chat.id
    temp.INVITE_LINK = None
    text = f"Success Fully Added:\n\nchat id: {chat.id}\nchat name: {chat.title}\nchat link: {link}"
    return await m.reply(text=text, disable_web_page_preview=True)
      
     
@Client.on_message(filters.command("get_sub") & filters.user(ADMINS))
async def get_sub(b, m):
    raw_id = await db.get_channel()
    try:
        chat = await b.get_chat(int(raw_id))
    except ChatAdminRequired:
        return await m.reply("Channel Parameter Invalid. Iam Not Having Full Admin Rights In Your Channel. Please Add Admin With Full Admin Permeation")
    except Exception as e:
        return await m.reply(f'Error {e}')
        
    try:
        link = (await b.create_chat_invite_link(int(chat.id))).invite_link
    except Exception as e:
        print(e)
        link = "None"
    req = "True" if temp.REQ_SUB else "False"
    text = f"Current F-Sub:\n\nchat id: {chat.id}\nchat name: {chat.title}\nchat link: [Click]({link})\nReq Sub: {req}"
    return await m.reply(text=text, disable_web_page_preview=True)
          
   
@Client.on_message(filters.command("req_sub") & filters.user(ADMINS))
async def set_if_req(b, m):
    if len(m.command) == 1:
        return await m.reply('please enter command with on/off eg: /req_sub on / off')

    on = ['true', 'on', 'yes', '1']
    off = ['false', 'off', 'no', '0']
    key = m.text.split(' ', 1)[1]

    if key.lower() in on:
        mode = "True"
        temp.REQ_SUB = True
    elif key.lower() in off:
        mode = "False"
        temp.REQ_SUB = False 
    else:
        return await m.reply('enter correct value\nif you need on? enter `/req_sub On or True or Yes`\nelse you need off? enter `/req_sub Off or False or No`')
    await db.set_req(mode)
    temp.INVITE_LINK = None
    return await m.reply(f'request force sub is {mode}')
        
@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def restarted_bot(b, m):
    await m.reply("Bot Restarting......")
    os.execl(sys.executable, sys.executable, *sys.argv)


@Client.on_message(filters.command('update') & filters.user(ADMINS))
async def update_code(b, m):
    os.system("git pull")
    await m.reply("Updated and Restarting..!")
    os.execl(sys.executable, sys.executable, "bot.py")


