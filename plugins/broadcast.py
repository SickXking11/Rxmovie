from pyrogram import Client, filters
from pyrogram.errors import InputUserDeactivated, FloodWait, UserIsBlocked, PeerIdInvalid
from database.users_chats_db import db
from info import ADMINS
import time, asyncio, datetime
        
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text(text='𝙱𝚁𝙾𝙰𝙳𝙲𝙰𝚂𝚃 𝙸𝙽𝙸𝚃𝙸𝙰𝚃𝙴𝙳..📯\n𝚈𝙾𝚄 𝚆𝙸𝙻𝙻 𝙱𝙴 𝙽𝙾𝚃𝙸𝙵𝙸𝙴𝙳 𝚆𝙸𝚃𝙷 𝙻𝙾𝙶 𝙵𝙸𝙻𝙴 𝚆𝙷𝙴𝙽 𝙰𝙻𝙻 𝚃𝙷𝙴 𝚄𝚂𝙴𝚁𝚂 𝙰𝚁𝙴 𝙽𝙾𝚃𝙸𝙵𝙸𝙴𝙳 🔉')
    total_users = await db.total_users_count()
    done = 0
    failed =0
    success = 0
    start_time = time.time()
    async for user in users:
        try:
            await b_msg.copy(chat_id=int(user['id']))
            success += 1
        except FloodWait as e:    
            await asyncio.sleep(e.value)
            await b_msg.copy(chat_id=int(user['id']))
            success += 1
        except InputUserDeactivated:
            await db.delete_user(int(user['id']))
            print(f"{user['id']} Removed from Database, since deleted account.")
            failed += 1 
        except UserIsBlocked:
            await db.delete_user(int(user['id']))    
            print(f"{user['id']} -Blocked the bot")
            failed += 1 
        except PeerIdInvalid:
            await db.delete_user(int(user['id']))
            print(f"{user['id']} - PeerIdInvalid")
            failed += 1 
        except Exception as e:
            print(f"{user['id']}\n{e}")
            failed += 1 
        done += 1
    completed_in = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.delete()
    await message.reply_text(text=f"""🚀 𝙱𝚁𝙾𝙰𝙳𝙲𝙰𝚂𝚃 𝙲𝙾𝙼𝙿𝙻𝙴𝚃𝙴𝙳 𝙸𝙽 - {completed_in}\n\n𝚃𝙾𝚃𝙰𝙻 𝚄𝚂𝙴𝚁𝚂 {total_users}.\n𝚃𝙾𝚃𝙰𝙻 𝙳𝙾𝙽𝙴 {done}, {success} 𝚂𝚄𝙲𝙲𝙴𝚂𝚂 & {failed} 𝙵𝙰𝙸𝙻𝙴𝙳""", quote=True)        
   
  
