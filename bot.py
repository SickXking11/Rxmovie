from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import BOT_TOKEN, API_ID, API_HASH, ADMINS
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types

from aiohttp import web
from route import web_server

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="AutoFilter",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )

    async def start(self):
        auth_channel = await db.get_channel()
        if await db.get_req(): temp.REQ_SUB = True
        else: REQ_SUB = False 
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        temp.AUTH_CHANNEL = auth_channel
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        self.mention = me.mention
        app = web.AppRunner(await web_server())
        await app.setup()        
        await web.TCPSite(app, "0.0.0.0", 8080).start()
        print(f"{me.first_name} 𝚂𝚃𝙰𝚁𝚃𝙴𝙳 ⚡️⚡️⚡️")
      
    async def stop(self, *args):
        await super().stop()      
        print("Bot Stopped")

    async def iter_messages(self, chat_id: Union[int, str], limit: int, offset: int = 0) -> Optional[AsyncGenerator["types.Message", None]]:       
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1



app = Bot()
app.run()
