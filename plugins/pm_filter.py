import asyncio
import re
import os
import ast
import math, logging, time
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active,  make_inactive
from info import DL_TIME, BTN, ADMINS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, CHANNEL_LINK, GROUP_LINK, OWNER
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, search_gagala, temp, get_settings, save_group_settings
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, db as fdb
from database.filters_mdb import del_all, find_filter, get_filters
from plugins.fsub import ForceSub

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}
PM_BUTTONS = {}
PM_SPELL_CHECK = {}

@Client.on_message(filters.group & filters.text & filters.incoming & filters.chat(AUTH_GROUPS) if AUTH_GROUPS else filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    k = await manual_filters(client, message)
    if k == False:
        await auto_filter(client, message)

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_give_filter(client, message):
    await pm_auto_filter(client, message)


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
       
    elif query.data.startswith("next"):
        await next_page(client, query)
        
    elif query.data.startswith("spolling"):
        await advantage_spoll_choker(client, query)
        
    elif query.data.startswith("pmnext"):
        await pm_next_page(client, query)
        
    elif query.data.startswith("pmspolling"):
        await pm_advantage_spoll_choker(client, query)
   
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer('Piracy Is Crime')
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer('Piracy Is Crime')

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer('Piracy Is Crime')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Bro Search Your Own File Don't Click Other Requested Files 😒", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer('Piracy Is Crime')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer('Piracy Is Crime')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('Piracy Is Crime')
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('Piracy Is Crime')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('Piracy Is Crime')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
            
    elif query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        try:
            req = query.message.reply_to_message.from_user.id
            if int(req) not in [query.from_user.id, 0]:
                return await query.answer("Hey This Is Not For You. Please Search You Self", show_alert=True)
        except:
            pass
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist. അയ്യോടാ മോനെ ആ file പോയല്ലോ ☹️. ഒന്നുകൂടെ ഗ്രൂപ്പിൽ പോയി button ക്ലിക്ക് ചെയ്യും')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        settings = await get_settings(query.message.chat.id)
        f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title, file_size='' if size is None else size)
           
        try:
            if not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False,
                    reply_markup=BTN
                )
                await query.answer('Check PM, I have sent files in pm', show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock the bot mahn !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
     
    
    elif query.data.startswith("pmfile"):
        ident, file_id = query.data.split("#")
        
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist. അയ്യോടാ മോനെ ആ file പോയല്ലോ ☹️. ഒന്നുകൂടെ ഗ്രൂപ്പിൽ പോയി button ക്ലിക്ക് ചെയ്യു')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        settings = await get_settings(query.message.chat.id)
        f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title, file_size='' if size is None else size)
        try:
            await client.send_cached_media(chat_id=query.from_user.id, file_id=file_id, caption=f_caption, reply_markup=BTN)
        except Exception as e:
            print(e)
           
    elif query.data.startswith("checksub"):
        if not await is_subscribed(client, query):
            await query.answer("I Like Your Smartness, But Don't Be Oversmart 😒.ചാനൽ subscribe ചെയ്ത ശേഷം Try Again എന്ന ബട്ടണിൽ ക്ലിക്ക് ചെയ്യുക 😁", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title, file_size='' if size is None else size)
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False,
            reply_markup=BTN
        )
    elif query.data == "pages":
        await query.answer("Please Click Movie Button Only 🙏", show_alert=True)

    elif query.data == "moviedl":
        await query.answer(script.MV_DL, show_alert=True)

    elif query.data == "nonmovie":
        await query.answer(script.NO_MV, show_alert=True)

    elif query.data == "start":
        buttons = [[ 
            InlineKeyboardButton('🔗 ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋs 🔗', url=CHANNEL_LINK)
            ],[
            InlineKeyboardButton('📯 ᴍʏ ɢʀᴏᴜᴘ', url=GROUP_LINK),
            InlineKeyboardButton('⚒️ ᴍʏ ᴏᴡɴᴇʀ', url=OWNER)
            ],[
            InlineKeyboardButton('⚠️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('⚙️ ᴀʙᴏᴜᴛ', callback_data='about')
            ],[
            InlineKeyboardButton("➕️ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕️", url=f"http://t.me/{temp.U_NAME}?startgroup=true")
            ],[
            InlineKeyboardButton('🔍 ꜱᴇᴀʀᴄʜ ᴍᴏᴠɪᴇ 🔎', switch_inline_query_current_chat='')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, client.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer('Piracy Is Crime')
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('ᴍᴀɴᴜᴀʟ ғɪʟᴛᴇʀ', callback_data='manuelfilter'),
            InlineKeyboardButton('ᴀᴜᴛᴏ ғɪʟᴛᴇʀ', callback_data='autofilter')
            ],[
            InlineKeyboardButton('ᴄᴏɴɴᴇᴄᴛɪᴏɴ', callback_data='coct'),
            InlineKeyboardButton('ᴀᴅᴍɪɴ ᴏɴʟʏ', callback_data='extra')
            ],[
            InlineKeyboardButton('🏠 ʜᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('🔮 sᴛᴀᴛᴜs', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('✨️ ᴄʜᴀɴɴᴇʟ', url=CHANNEL_LINK),
        ],[
            InlineKeyboardButton('🏠 ʜᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('🔐 ᴄʟᴏsᴇ', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(client.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('ʙᴜᴛᴛᴏɴ ғᴏʀᴍᴀᴛ', callback_data='button')
            ],[
            InlineKeyboardButton('< ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('< ʙᴀᴄᴋ', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('< ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('< ʙᴀᴄᴋ', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('< ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('ᴀᴅᴍɪɴ ᴄᴍᴅ', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )  
    elif query.data == "admin":
        if query.from_user.id in ADMINS:        
            await query.message.edit_text(text=script.ADMIN_TXT, reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('👩‍🦯 ʙᴀᴄᴋ', callback_data='extra')]]), parse_mode=enums.ParseMode.HTML)
        else:         
            await query.answer("𝚂𝙾𝚁𝚁𝚈 𝙳𝚄𝙳𝙴 𝚈𝙾𝚄'𝚁 𝙽𝙾𝚃 𝙰𝙳𝙼𝙸𝙽", show_alert=True)                      
    elif query.data == "stats":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('< ʙᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('♻️ ʀᴇғʀᴇsʜ', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
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
        await query.message.edit_text("ᴡᴀɪᴛ.....")
        await query.message.edit_text(
            text=script.STATUS_TXT.format(
                users=users,
                chats=chats,
                used=monsize,
                free=free,
                total=total,
                fused=fmonsize,
                ffree=ffree),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer('Piracy Is Crime')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [[
                InlineKeyboardButton('ʙᴜᴛᴛᴏɴ', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                InlineKeyboardButton('sɪɴɢʟᴇ' if settings["button"] else 'ᴅᴏᴜʙʟᴇ', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],[
                InlineKeyboardButton('ʙᴏᴛ ᴘᴍ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ ᴏɴ' if settings["botpm"] else '❌ ᴏғғ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],[
                InlineKeyboardButton('ʀᴇsᴛʀɪᴄ ᴄᴏɴᴛᴇɴᴛ', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ ᴏɴ' if settings["file_secure"] else '❌ ᴏғғ', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],[
                InlineKeyboardButton('sᴘᴇʟʟ ᴄʜᴇᴄᴋ', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ ᴏɴ' if settings["spell_check"] else '❌ ᴏғғ', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],[
                InlineKeyboardButton('ᴡᴇʟᴄᴏᴍᴇ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ ᴏɴ' if settings["welcome"] else '❌ ᴏғғ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer('Piracy Is Crime')


async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(msg)
                else:
                    return
        else:
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}]🔹{file.file_name}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
            ]
            for file in files
        ]
    btn.insert(0, 
        [
            InlineKeyboardButton("❄︎ 𝙷𝙾𝚆 𝚃𝙾 𝙳𝙾𝚆𝙽𝙻𝙾𝙰𝙳 𝙼𝙾𝚅𝙸𝙴𝚂 ❄︎", url="https://t.me/downloadmovieshow/2")
        ]
    )

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="ɴᴇxᴛ ⏩", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )
    
    cap = f"Here is what i found for your query {search}"
    try:
        ab=await message.reply_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True) 
        if spoll: await msg.message.delete()
        await asyncio.sleep(DL_TIME)
        await ab.delete()   
    except FloodWait:
        await asyncio.sleep(FloodWait.value)
        ab=await message.reply_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True) 
        if spoll: await msg.message.delete()
        await asyncio.sleep(DL_TIME)
        await ab.delete()   
    except Exception as e:
        logger.exception(e)
        cd=await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        if spoll: await msg.message.delete()
        await asyncio.sleep(DL_TIME)
        await cd.delete()     
   
  
  
async def pm_auto_filter(client, msg, spoll=False):
    if not await is_subscribed(client, msg):
        return await ForceSub(client, msg)
        
    if not spoll:
        message = msg
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text): return
        if not 2 < len(message.text) < 100: return 
        search = message.text
        files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
        if not files:
            return await pm_advantage_spell_chok(msg)
                
    else:
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
       
    btn = [[
        InlineKeyboardButton(text=f"[{get_size(file.file_size)}]🔹{file.file_name}", callback_data=f"pmfile#{file.file_id}"),
    ] for file in files]
        
    btn.insert(0, 
        [InlineKeyboardButton("❄︎ 𝙷𝙾𝚆 𝚃𝙾 𝙳𝙾𝚆𝙽𝙻𝙾𝙰𝙳 𝙼𝙾𝚅𝙸𝙴𝚂 ❄︎", url="https://t.me/downloadmovieshow/2")]
    )

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        PM_BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="ɴᴇxᴛ ⏩", callback_data=f"pmnext_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )
    
    cap = f"Here is what i found for your query {search}"
    try:
        ab=await message.reply_text(text=cap, quote=True, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True) 
        if spoll: await msg.message.delete()
        await asyncio.sleep(DL_TIME)
        await ab.delete()   
    except FloodWait:
        await asyncio.sleep(FloodWait.value)
        ab=await message.reply_text(text=cap, quote=True, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True) 
        if spoll: await msg.message.delete()
        await asyncio.sleep(DL_TIME)
        await ab.delete()   
    except Exception as e:
        logger.exception(e)
        cd=await message.reply_text(cap, quote=True, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        if spoll: await msg.message.delete()
        await asyncio.sleep(DL_TIME)
        await cd.delete()     
    



async def advantage_spell_chok(msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    try:
        g_s = await search_gagala(query)
    except Exception as e:
        print(e)
    #g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        k = await msg.reply(
            text="""✯ നിങ്ങൾ ചോദിച്ച മൂവി റിലീസ് ആയിട്ടുണ്ടോ..? \n\n✯ 𝗜𝗳 𝗶𝘁 𝗶𝘀 , 𝗪𝗲 𝗪𝗶𝗹𝗹 𝗨𝗽𝗹𝗼𝗮𝗱 𝗜𝘁⚡️\n\n📯ɴʙ: Cʟɪᴄᴋ Bᴇʟᴏᴡ Rᴇᴀsᴏɴs Bᴜᴛᴛᴏɴ""",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="★ 𝗥𝗘𝗔𝗦𝗢𝗡𝗦 ★", callback_data="nonmovie")]])
        )
        await asyncio.sleep(20)
        return await k.delete()
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(
        r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)',
        '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
                         re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        try: from imdb import IMDb
        except: pass
        for mov in gs_parsed: 
            mov = mov.strip()
            imdb_s = IMDb().search_movie(mov.lower(), results=10)
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]
            
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if not movielist:
        k = await msg.reply("""<b>‼️ FILE NOT FOUND ? ‼️

I couldn't find anything related to that. Check your spelling.

1⃣ നിങ്ങൾ type ചെയ്ത സിനിമയുടെ സ്പെല്ലിങ്ങ് ഗൂഗിളിൽ ഉള്ളത് പോലെ ആണോ എന്ന് ഉറപ്പ് വരുത്തുക.

2⃣ നിങ്ങൾ ചോദിച്ച സിനിമ OTT റിലീസ് ആയതാണോ എന്ന് ചെക്ക് ചെയ്യുക.

3⃣ മൂവിക്ക് വേണ്ടി മെസ്സേജ് അയക്കുമ്പോൾ മൂവിയുടെ പേര് ഇറങ്ങിയ വർഷം മാത്രം അയക്കുക..!!</b>""")
        await asyncio.sleep(8)
        await k.delete()
        return
    SPELL_CHECK[msg.id] = movielist
    btn = [[
        InlineKeyboardButton(
            text=movie.strip(),
            callback_data=f"spolling#{user}#{k}",
        )
    ] for k, movie in enumerate(movielist)]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    abir=await msg.reply("<b>✯ നിങ്ങൾ ഉദ്ദേശിച്ച മൂവി താഴെ കാണുന്ന വല്ലതും ആണ് എങ്കിൽ.അതിൽ ക്ലിക്ക് ചെയ്യുക \n\n✯ ɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴀɴʏᴛʜɪɴɢ ʀᴇʟᴀᴛᴇᴅ ᴛᴏ ᴛʜᴀᴛ ᴅɪᴅ ʏᴏᴜ ᴍᴇᴀɴ ᴀɴʏ ᴏɴᴇ ᴏꜰ ᴛʜᴇꜱᴇ?\n\n📯 𝗡𝗕 : ᴄʟɪᴄᴋ ᴛʜᴇ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ ᴏɴʟʏ ᴅᴏɴᴛ ᴜꜱᴇ ʏᴇᴀʀ ʙᴜᴛᴛᴏɴ.</b>",
                    reply_markup=InlineKeyboardMarkup(btn))
    await asyncio.sleep(DL_TIME)
    await abir.delete()    



async def pm_advantage_spell_chok(msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    try:
        g_s = await search_gagala(query)
    except Exception as e:
        print(e)
    #g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        k = await msg.reply(
            text="""✯ നിങ്ങൾ ചോദിച്ച മൂവി റിലീസ് ആയിട്ടുണ്ടോ..? \n\n✯ 𝗜𝗳 𝗶𝘁 𝗶𝘀 , 𝗪𝗲 𝗪𝗶𝗹𝗹 𝗨𝗽𝗹𝗼𝗮𝗱 𝗜𝘁⚡️\n\n📯ɴʙ: Cʟɪᴄᴋ Bᴇʟᴏᴡ Rᴇᴀsᴏɴs Bᴜᴛᴛᴏɴ""",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="★ 𝗥𝗘𝗔𝗦𝗢𝗡𝗦 ★", callback_data="nonmovie")]])
        )
        await asyncio.sleep(20)
        return await k.delete()
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(
        r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)',
        '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
                         re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    if gs_parsed:
        try: from imdb import IMDb
        except: pass
        for mov in gs_parsed: 
            mov = mov.strip()
            imdb_s = IMDb().search_movie(mov.lower(), results=10)
            if imdb_s:
                movielist += [movie.get('title') for movie in imdb_s]
            
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if not movielist:
        k = await msg.reply("""<b>‼️ FILE NOT FOUND ? ‼️

I couldn't find anything related to that. Check your spelling.

1⃣ നിങ്ങൾ type ചെയ്ത സിനിമയുടെ സ്പെല്ലിങ്ങ് ഗൂഗിളിൽ ഉള്ളത് പോലെ ആണോ എന്ന് ഉറപ്പ് വരുത്തുക.

2⃣ നിങ്ങൾ ചോദിച്ച സിനിമ OTT റിലീസ് ആയതാണോ എന്ന് ചെക്ക് ചെയ്യുക.

3⃣ മൂവിക്ക് വേണ്ടി മെസ്സേജ് അയക്കുമ്പോൾ മൂവിയുടെ പേര് ഇറങ്ങിയ വർഷം മാത്രം അയക്കുക..!!</b>""")
        await asyncio.sleep(8)
        await k.delete()
        return
    PM_SPELL_CHECK[msg.id] = movielist
    btn = [[
        InlineKeyboardButton(
            text=movie.strip(),
            callback_data=f"pmspolling#{user}#{k}",
        )
    ] for k, movie in enumerate(movielist)]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    abir=await msg.reply("<b>✯ നിങ്ങൾ ഉദ്ദേശിച്ച മൂവി താഴെ കാണുന്ന വല്ലതും ആണ് എങ്കിൽ.അതിൽ ക്ലിക്ക് ചെയ്യുക \n\n✯ ɪ ᴄᴏᴜʟᴅɴ'ᴛ ꜰɪɴᴅ ᴀɴʏᴛʜɪɴɢ ʀᴇʟᴀᴛᴇᴅ ᴛᴏ ᴛʜᴀᴛ ᴅɪᴅ ʏᴏᴜ ᴍᴇᴀɴ ᴀɴʏ ᴏɴᴇ ᴏꜰ ᴛʜᴇꜱᴇ?\n\n📯 𝗡𝗕 : ᴄʟɪᴄᴋ ᴛʜᴇ ᴍᴏᴠɪᴇ ɴᴀᴍᴇ ᴏɴʟʏ ᴅᴏɴᴛ ᴜꜱᴇ ʏᴇᴀʀ ʙᴜᴛᴛᴏɴ.</b>",
                    quote=True, reply_markup=InlineKeyboardMarkup(btn))
    await asyncio.sleep(DL_TIME)
    await abir.delete()    




async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")                     
            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            owl=await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id)
                            await asyncio.sleep(DL_TIME)
                            await owl.delete()     
                        else:
                            button = eval(btn)
                            dark=await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                            await asyncio.sleep(DL_TIME)
                            await dark.delete()     
                    elif btn == "[]":
                        fkk=await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                        await asyncio.sleep(DL_TIME)
                        await fkk.delete()     
                    else:
                        button = eval(btn)
                        njan=await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        await asyncio.sleep(DL_TIME)
                        await njan.delete()     
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False


async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("Bro Search Your Own Don't Click Other Requested Files 😒", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    if settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}]🔹{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]
    btn.insert(0, 
        [
            InlineKeyboardButton("❄︎ 𝙷𝙾𝚆 𝚃𝙾 𝙳𝙾𝚆𝙽𝙻𝙾𝙰𝙳 𝙼𝙾𝚅𝙸𝙴𝚂 ❄︎", url="https://t.me/downloadmovieshow/2")
        ]
    )

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 ᴩᴀɢᴇꜱ {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("ɴᴇxᴛ ⏩", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("ɴᴇxᴛ ⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


async def pm_next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("Bro Search Your Own Don't Click Other Requested Files 😒", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = PM_BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    
    btn = [[
        InlineKeyboardButton(text=f"[{get_size(file.file_size)}]🔹{file.file_name}", callback_data=f"pmfile#{file.file_id}"),
    ] for file in files]
        
    btn.insert(0, 
        [InlineKeyboardButton("❄︎ 𝙷𝙾𝚆 𝚃𝙾 𝙳𝙾𝚆𝙽𝙻𝙾𝙰𝙳 𝙼𝙾𝚅𝙸𝙴𝚂 ❄︎", url="https://t.me/downloadmovieshow/2")]
    )

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ ʙᴀᴄᴋ", callback_data=f"pmnext_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 ᴩᴀɢᴇꜱ {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("ɴᴇxᴛ ⏩", callback_data=f"pmnext_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ ʙᴀᴄᴋ", callback_data=f"pmnext_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("ɴᴇxᴛ ⏩", callback_data=f"pmnext_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("Bro Search Your Own Don't Click Other Requested Files 😒", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer("You are clicking on an old button which is expired. ബ്രോ മറ്റുള്ളവർ റിക്യസ്റ്റ് ചെയ്ത മൂവിയിൽ കുത്തി നോക്കാതെ ബ്രോന് വേണ്ടത് ബ്രോ റിക്യസ്റ്റ് ചെയ്യുക.🤒 ", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Checking for Movie in database...')
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            k = await query.message.edit('This Movie Not Found In DataBase. Sorry ആ മൂവി ചിലപ്പോൾ release ആയിട്ടുണ്ടാവില്ല. അല്ലെങ്കിൽ അത് ഞങ്ങളുടെ database ഇൽ ഇല്ല 🙏🥺')
            await asyncio.sleep(10)
            await k.delete()


async def pm_advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("Bro Search Your Own Don't Click Other Requested Files 😒", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = PM_SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer("You are clicking on an old button which is expired. ബ്രോ മറ്റുള്ളവർ റിക്യസ്റ്റ് ചെയ്ത മൂവിയിൽ കുത്തി നോക്കാതെ ബ്രോന് വേണ്ടത് ബ്രോ റിക്യസ്റ്റ് ചെയ്യുക.🤒 ", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Checking for Movie in database...')
    
    files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
    if files:
        k = (movie, files, offset, total_results)
        await pm_auto_filter(bot, query, k)
    else:
        k = await query.message.edit('This Movie Not Found In DataBase. Sorry ആ മൂവി ചിലപ്പോൾ release ആയിട്ടുണ്ടാവില്ല. അല്ലെങ്കിൽ അത് ഞങ്ങളുടെ database ഇൽ ഇല്ല 🙏🥺')
        await asyncio.sleep(10)
        await k.delete()





