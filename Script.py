class script(object):
    START_TXT = """<b>Hᴇʏ {}

Mʏ Nᴀᴍᴇ Iꜱ {}
   
I Cᴀɴ Pʀᴏᴠɪᴅᴇ Aʟʟ Mᴏᴠɪᴇꜱ Oɴ Mʏ Gʀᴏᴜᴩ. I Aᴍ Oɴʟʏ Wᴏʀᴋ Iɴ Mʏ Gʀᴏᴜᴩ.
Dᴏ Yᴏᴜ Nᴇᴇᴅ Mᴏᴠɪᴇꜱ? Pʟᴇᴀꜱᴇ Jᴏɪɴ Mʏ Gʀᴏᴜᴩ Aɴᴅ Sᴇɴᴅ Tʜᴇ Mᴏᴠɪᴇ Nᴀᴍᴇ</b>"""
  
    HELP_TXT = "Hᴇʟᴩ Mᴇɴᴜ Fᴏʀ Yᴏᴜ"

    ABOUT_TXT = """<b>Mʏ Nᴀᴍᴇ: {}
Mʏ Cʀᴇᴀᴛᴏʀ: <a href='https://t.me/Aug_PaidPromoter'>Oᴡɴᴇʀ</a>
Mʏ Sᴇʀᴠᴇʀ:  <a href='https://heroku.com'>Hᴇʀᴏᴋᴜ</a>
Mʏ Dᴀᴛᴀʙᴀꜱᴇ:  <a href='https://mongodb.com'>Mᴏɴɢᴏ Dʙ</a>
Mʏ Pʀᴏɢʀᴀᴍ:  <a href=https://pyrogram.org>Pʏʀᴏɢʀᴀᴍ</a></b>"""

    MANUELFILTER_TXT = """Help: <b>Filters</b>

- Filter is the feature were users can set automated replies for a particular keyword and bot will respond whenever a keyword is found the message

<b>NOTE:</b>
1. bot should have admin privillage.
2. only admins can add filters in a chat.
3. alert buttons have a limit of 64 characters.

<b>Commands and Usage:</b>
• /filter - <code>add a filter in chat</code>
• /filters - <code>list all the filters of a chat</code>
• /del - <code>delete a specific filter in chat</code>
• /delall - <code>delete the whole filters in a chat (chat owner only)</code>"""
    BUTTON_TXT = """Help: <b>Buttons</b>

- Supports both url and alert inline buttons.

<b>NOTE:</b>
1. Telegram will not allows you to send buttons without any content, so content is mandatory.
2. supports buttons with any telegram media type.
3. Buttons should be properly parsed as markdown format

<b>URL buttons:</b>
<code>[Button Text](buttonurl:https://t.me/xxxxxxx)</code>

<b>Alert buttons:</b>
<code>[Button Text](buttonalert:This is an alert message)</code>"""
    AUTOFILTER_TXT = """Help: <b>Auto Filter</b>

<b>NOTE:</b>
1. Make me the admin of your channel if it's private.
2. make sure that your channel does not contains camrips, porn and fake files.
3. Forward the last message to me with quotes.
 I'll add all the files in that channel to my db."""
    CONNECTION_TXT = """Help: <b>Connections</b>

- Used to connect bot to PM for managing filters 
- it helps to avoid spamming in groups.

<b>NOTE:</b>
1. Only admins can add a connection.
2. Send <code>/connect</code> for connecting me to ur PM

<b>Commands and Usage:</b>
• /connect  - <code>connect a particular chat to your PM</code>
• /disconnect  - <code>disconnect from a chat</code>
• /connections - <code>list all your connections</code>"""
    EXTRAMOD_TXT = """Help: <b>Extra Modules</b>

<b>NOTE:</b>
these are the extra features of Eva Maria

<b>Commands and Usage:</b>
• /id - <code>get id of a specified user.</code>
• /info  - <code>get information about a user.</code>
• /imdb  - <code>get the film information from IMDb source.</code>
• /search  - <code>get the film information from various sources.</code>"""
    ADMIN_TXT = """Help: <b>Admin mods</b>

<b>NOTE:</b>
This module only works for my admins

<b>Commands and Usage:</b>
• /logs - <code>to get the rescent errors</code>
• /stats - <code>to get status of files in db.</code>
• /delete - <code>to delete a specific file from db.</code>
• /users - <code>to get list of my users and ids.</code>
• /chats - <code>to get list of the my chats and ids </code>
• /leave  - <code>to leave from a chat.</code>
• /disable  -  <code>do disable a chat.</code>
• /ban  - <code>to ban a user.</code>
• /unban  - <code>to unban a user.</code>
• /channel - <code>to get list of total connected channels</code>
• /broadcast - <code>to broadcast a message to all users</code>"""

    STATUS_TXT = """<b>Tᴏᴛᴀʟ Uꜱᴇʀꜱ: {users}
Tᴏᴛᴀʟ Cʜᴀᴛꜱ: {chats}
Dʙ Uꜱᴇᴅ Sɪᴢᴇ: {used}
Dʙ Fʀᴇᴇ Sɪᴢᴇ: {free}

Tᴏᴛᴀʟ Fɪʟᴇꜱ: {total}
Fɪʟᴇ Dʙ Uꜱᴇᴅ: {fused}
Fɪʟᴇ Dʙ Fʀᴇᴇ: {ffree}</b>"""

    LOG_TEXT_G = """#NewGroup
chat name = {n}
chat id = <code>{id}</code>
Total Members = <code>{tot}</code>
chat username = @{u}


Added By = {r}
"""

    LOG_TEXT_P = """#NewUser
ID - <code>{}</code>
Name - {}
"""

    NO_MV = """🌟 Check OTT Release Or Correct The spelling 

🌟 Don't Use Symbols While Request (.:;/|!?'...) 

🌟 [ Movie Name + Year ] Ask the Way

🌟 Don't Use Stylish Fonts """

    MV_DL = """✯ 𝗦𝘁𝗲𝗽 1 : Send the name of the movie with correct spelling
  
✯ 𝗦𝘁𝗲𝗽 2 : Click on the Button of the Movie you want
    
✯ 𝗦𝘁𝗲𝗽 3 : Then click " 𝗦𝗧𝗔𝗥𝗧 " on the Bot andyou will get the movie"""


    FSUB_TXT = """**♦️ READ THIS INSTRUCTION ♦️
  
🗣 നിങ്ങൾ ചോദിക്കുന്ന സിനിമകൾ നിങ്ങൾക്ക് ലഭിക്കണം എന്നുണ്ടെങ്കിൽ നിങ്ങൾ ഞങ്ങളുടെ ചാനലിൽ ജോയിൻ ചെയ്തിരിക്കണം. ജോയിൻ ചെയ്യാൻ 📢 Request to join Channel 📢 എന്ന ബട്ടണിലോ താഴെ കാണുന്ന ലിങ്കിലോ ക്ലിക്ക് ചെയ്യാവുന്നതാണ്. Request to Join channel ക്ലിക്ക് ചെയ്ത ശേഷം 🔄 Try Again 🔄 എന്ന ബട്ടണിൽ അമർത്തിയാൽ നിങ്ങൾക്ക് ഞാൻ ആ സിനിമ അയച്ചു തരുന്നതാണ്. 😍

🗣 In Order To Get The Movie Requested By You in Our Group, You Must Have To Join Our Official Channel First By Clicking 📢 Request to Join Channel 📢 Button or the Link shown Below. After That, Click 🔄 Try Again 🔄 Button. I'll Send You That Movie 🙈

👇 CLICK REQUEST TO JOIN CHANNEL & CLICK TRY AGAIN 👇**"""
        