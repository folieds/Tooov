# +++ Customised By Rohit [telegram username: @rohit_1888] +++

import os
import sys
import random
import asyncio
import subprocess
from bot import Bot
from database.database import db
from database.db_verify import *
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from plugins.FORMATS import *
from plugins.autoDelete import auto_del_notification, delete_message
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from helper_func import *


# +++ Customised By Rohit [telegram username: @rohit_1888] +++

@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id

    # Default initialization
    AUTO_DEL = False
    DEL_TIMER = 0
    HIDE_CAPTION = False
    CHNL_BTN = None
    PROTECT_MODE = False
    last_message = None
    messages = []

    VERIFY_EXPIRE = await db.get_verified_time()  # Fetch verification expiration time
    SHORTLINK_URL = await db.get_shortener_url()
    SHORTLINK_API = await db.get_shortener_api()
    TUT_VID = await db.get_tut_video()
    ADMINS = await db.get_all_admins()

    logging.info(f"Received /start command from user ID: {id}")

    # Check and add user to the database if not present
    if not await db.present_user(id):
        try:
            await db.add_user(id)
        except Exception as e:
            logging.error(f"Error adding user: {e}")
            return

    text = message.text

    # Check if user is an admin and treat them as verified
    if id in ADMINS:
        verify_status = {
            'is_verified': True,
            'verify_token': None,  # Admins don't need a token
            'verified_time': time.time(),
            'link': ""
        }
    else:
        verify_status = await get_verify_status(id)
    #verify_status = await get_verify_status(id)


    if SHORTLINK_URL:
        # Check if token has expired
        if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
            await update_verify_status(id, is_verified=False)
            logging.info(f"User {id} token expired, verification reset.")

        if "verify_" in message.text:
            _, token = message.text.split("_", 1)
            logging.info(f"User {id} entered token: {token}")

            if verify_status['verify_token'] != token:
                logging.warning(f"User {id} entered invalid token: {token}")
                return await message.reply("<blockquote>Yᴏᴜʀ ᴛᴏᴋᴇɴ ɪs ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ. Tʀʏ ᴀɢᴀɪɴ ʙʏ ᴄʟɪᴄᴋɪɴɢ /start</blockquote>")

            await update_verify_status(id, is_verified=True, verified_time=time.time())
            logging.info(f"User {id} successfully verified with token: {token}")

            return await message.reply(
                f"<blockquote>Yᴏᴜʀ ᴛᴏᴋᴇɴ ʜᴀs ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ ᴠᴇʀɪғɪᴇᴅ ᴀɴᴅ ɪs ᴠᴀʟɪᴅ ғᴏʀ {get_exp_time(VERIFY_EXPIRE)}</blockquote>",
                protect_content=False,
                quote=True
            )

        if not verify_status['is_verified']:
            token = ''.join(random.choices(rohit.ascii_letters + rohit.digits, k=10))
            await update_verify_status(id, verify_token=token, link="")
            logging.info(f"Nᴇᴡ ᴛᴏᴋᴇɴ ɢᴇɴᴇʀᴀᴛᴇᴅ ғᴏʀ ᴜsᴇʀ {id}: {token}")

            link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://telegram.dog/{client.username}?start=verify_{token}')
            logging.info(f"Verification link for user {id}: {link}")

            return await message.reply_photo(
                photo=TOKEN_PIC,
                caption=f"<b><blockquote>Yᴏᴜʀ ᴛᴏᴋᴇɴ ʜᴀs ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀsᴇ ʀᴇғʀᴇsʜ ʏᴏᴜʀ ᴛᴏᴋᴇɴ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.</blockquote>\n"
                        f"<blockquote>Tᴏᴋᴇɴ ᴛɪᴍᴇᴏᴜᴛ : {get_exp_time(VERIFY_EXPIRE)}</blockquote>\n\n"
                        f"<blockquote>Wʜᴀᴛ ɪs ᴛʜᴇ ᴛᴏᴋᴇɴ?</blockquote>\n"
                        f"<blockquote>Tʜɪs ɪs ᴀɴ ᴀᴅs ᴛᴏᴋᴇɴ. ᴘᴀssɪɴɢ ᴏɴᴇ ᴀᴅ ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ ғᴏʀ {get_exp_time(VERIFY_EXPIRE)}</blockquote>\n</b>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Vᴇʀɪғʏ ʜᴇʀᴇ", url=link)],
                     [InlineKeyboardButton("Tᴜᴛᴏʀɪᴀʟ", url=TUT_VID)]
                ])
            )
                
    text = message.text        
    if len(text)>7:
        await message.delete()

        try: base64_string = text.split(" ", 1)[1]
        except: return
                
        string = await decode(base64_string)
        argument = string.split("-")
        
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
                    
            if start <= end:
                ids = range(start,end+1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
                            
        elif len(argument) == 2:
            try: ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except: return
                    
        last_message = None
        await message.reply_chat_action(ChatAction.UPLOAD_DOCUMENT)  
        
        try: messages = await get_messages(client, ids)
        except: return await message.reply("<b><i>sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ..!</i></b>")
            
        AUTO_DEL, DEL_TIMER, HIDE_CAPTION, CHNL_BTN, PROTECT_MODE = await asyncio.gather(db.get_auto_delete(), db.get_del_timer(), db.get_hide_caption(), db.get_channel_button(), db.get_protect_content())   
        if CHNL_BTN: button_name, button_link = await db.get_channel_button_link()
            
        for idx, msg in enumerate(messages):
            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)

            elif HIDE_CAPTION and (msg.document or msg.audio):
                caption = ""

            else:
                caption = "" if not msg.caption else msg.caption.html

            if CHNL_BTN:
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=button_name, url=button_link)]]) if msg.document or msg.photo or msg.video or msg.audio else None
            else:
                reply_markup = msg.reply_markup   
                    
            try:
                copied_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_MODE)
                await asyncio.sleep(0.1)

                if AUTO_DEL:
                    asyncio.create_task(delete_message(copied_msg, DEL_TIMER))
                    if idx == len(messages) - 1: last_message = copied_msg

            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(chat_id=id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_MODE)
                await asyncio.sleep(0.1)
                
                if AUTO_DEL:
                    asyncio.create_task(delete_message(copied_msg, DEL_TIMER))
                    if idx == len(messages) - 1: last_message = copied_msg
                        
        if AUTO_DEL and last_message:
                asyncio.create_task(auto_del_notification(client.username, last_message, DEL_TIMER, message.command[1]))
                        
    else:   
        reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("•  ғᴏʀ ᴍᴏʀᴇ  •", callback_data='about')],
                    [InlineKeyboardButton("• sᴇᴛᴛɪɴɢs", callback_data='setting'),
                     InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ •", url='https://t.me/URR_SANJIII')],
                ])
        await message.reply_photo(
            photo = random.choice(PICS),
            caption = START_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
            reply_markup = reply_markup,
	        message_effect_id=5104841245755180586 #🔥
        )
        try: await message.delete()
        except: pass

   
##===================================================================================================================##

#TRIGGRED START MESSAGE FOR HANDLE FORCE SUB MESSAGE AND FORCE SUB CHANNEL IF A USER NOT JOINED A CHANNEL

##===================================================================================================================##   


# Create a global dictionary to store chat data
chat_data_cache = {}

@Bot.on_message(filters.command('start') & filters.private & ~banUser)
async def not_joined(client: Client, message: Message):
    temp = await message.reply(f"<b>??</b>")
    
    user_id = message.from_user.id
               
    REQFSUB = await db.get_request_forcesub()
    buttons = []
    count = 0

    try:
        for total, chat_id in enumerate(await db.get_all_channels(), start=1):
            await message.reply_chat_action(ChatAction.PLAYING)
            
            # Show the join button of non-subscribed Channels.....
            if not await is_userJoin(client, user_id, chat_id):
                try:
                    # Check if chat data is in cache
                    if chat_id in chat_data_cache:
                        data = chat_data_cache[chat_id]  # Get data from cache
                    else:
                        data = await client.get_chat(chat_id)  # Fetch from API
                        chat_data_cache[chat_id] = data  # Store in cache
                    
                    cname = data.title
                    
                    # Handle private channels and links
                    if REQFSUB and not data.username: 
                        link = await db.get_stored_reqLink(chat_id)
                        await db.add_reqChannel(chat_id)
                        
                        if not link:
                            link = (await client.create_chat_invite_link(chat_id=chat_id, creates_join_request=True)).invite_link
                            await db.store_reqLink(chat_id, link)
                    else:
                        link = data.invite_link

                    # Add button for the chat
                    buttons.append([InlineKeyboardButton(text='››  ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ  ×', url=link)])
                    count += 1
                    await temp.edit(f"<b>{'! ' * count}</b>")
                                                            
                except Exception as e:
                    print(f"Can't Export Channel Name and Link..., Please Check If the Bot is admin in the FORCE SUB CHANNELS:\nProvided Force sub Channel:- {chat_id}")
                    return await temp.edit(f"<b><i>! ᴇʀʀᴏʀ, ᴄᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @Urr_Sanjiii</i></b>\n<blockquote expandable><b>ʀᴇᴀsᴏɴ:</b> {e}</blockquote>")

        try:
            buttons.append([InlineKeyboardButton(text='‼️ ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ ‼️', url=f"https://t.me/{client.username}?start={message.command[1]}")])
        except IndexError:
            pass

        await message.reply_chat_action(ChatAction.CANCEL)
        await temp.edit_media(
            media=InputMediaPhoto(
                random.choice(PICS),
                caption=FORCE_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=None if not message.from_user.username else '@' + message.from_user.username,
                    mention=message.from_user.mention,
                    id=message.from_user.id,
                    count=count,
                    total=total
                )
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
                
        try: await message.delete()
        except: pass
                        
    except Exception as e:
        print(f"Unable to perform forcesub buttons reason : {e}")
        return await temp.edit(f"<b><i>! ᴇʀʀᴏʀ, ᴄᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @Urr_Sanjiii</i></b>\n<blockquote expandable><b>ʀᴇᴀsᴏɴ:</b> {e}</blockquote>")

# +++ Customised By Rohit [telegram username: @rohit_1888] +++

#=====================================================================================##
#......... RESTART COMMAND FOR RESTARTING BOT .......#
#=====================================================================================##

@Bot.on_message(filters.command('restart') & filters.private & filters.user(OWNER_ID))
async def restart_bot(client: Client, message: Message):
    print("Restarting bot...")
    msg = await message.reply(text=f"<b><i>⚠️ {client.name} ɢᴏɪɴɢ ᴛᴏ ʀᴇsᴛᴀʀᴛ...</i></b>")
    try:
        await asyncio.sleep(6)  # Wait for 6 seconds before restarting
        await msg.delete()
        args = [sys.executable, "main.py"]  # Adjust this if your start file is named differently
        os.execl(sys.executable, *args)
    except Exception as e:
        print(f"Error occured while Restarting the bot: {e}")
        return await msg.edit_text(f"<b><i>! ᴇʀʀᴏʀ, ᴄᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @Urr_Sanjiii</i></b>\n<blockquote expandable><b>ʀᴇᴀsᴏɴ:</b> {e}</blockquote>")
    # Optionally, you can add cleanup tasks here
    #subprocess.Popen([sys.executable, "main.py"])  # Adjust this if your start file is named differently
    #sys.exit()
