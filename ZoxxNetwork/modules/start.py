import random
from html import escape 

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler

from ZoxxNetwork import application, PHOTO_URL, SUPPORT_CHAT, UPDATE_CHAT, BOT_USERNAME, db, GROUP_ID
from ZoxxNetwork import pm_users as collection 


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    # USER DATABASE CHECK
    user_data = await collection.find_one({"_id": user_id})

    if user_data is None:
        await collection.insert_one(
            {"_id": user_id, "first_name": first_name, "username": username}
        )

        await context.bot.send_message(
            chat_id=GROUP_ID, 
            text=(
                f"ɴᴇᴡ ᴜsᴇʀ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ..\n"
                f"ᴜsᴇʀ: <a href='tg://user?id={user_id}'>{escape(first_name)}</a>"
            ),
            parse_mode='HTML'
        )
    else:
        if user_data['first_name'] != first_name or user_data['username'] != username:
            await collection.update_one(
                {"_id": user_id},
                {"$set": {"first_name": first_name, "username": username}}
            )

    # ========================= PRIVATE ============================
    if update.effective_chat.type == "private":

        caption = f"""
         ***ʜᴇʏʏʏʏ...***

***ɪ ᴀᴍ ɢʀᴀʙʙɪɴɢ ʏᴏᴜʀ ᴡᴀɪғᴜ ʙᴏᴛ...ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.. ᴀɴᴅ ɪ ᴡɪʟʟ sᴇɴᴅ ʀᴀɴᴅᴏᴍ ᴄʜᴀʀᴀᴄᴛᴇʀs ᴀғᴛᴇʀ.. ᴇᴠᴇʀʏ 100 ᴍᴇssᴀɢᴇs ɪɴ ɢʀᴏᴜᴘ... ᴜsᴇ /grab ᴛᴏ.. ᴄᴏʟʟᴇᴄᴛ ᴛʜᴀᴛ ᴄʜᴀᴛʀᴀᴄᴛᴇʀs ɪɴ ʏᴏᴜʀ ᴄᴏʟʟᴇᴄᴛɪᴏɴ.. ᴀɴᴅ sᴇᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ʙʏ ᴜsɪɴɢ /Harem... sᴏ ᴀᴅᴅ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘs ᴀɴᴅ ᴄᴏʟʟᴇᴄᴛ ʏᴏᴜʀ ʜᴀʀᴇᴍ***
        """

        keyboard = [
            [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f'http://t.me/{BOT_USERNAME}?startgroup=new')],
            [
                InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=f'https://t.me/{SUPPORT_CHAT}'),
                InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url=f'https://t.me/{UPDATE_CHAT}')
            ],
            [
                InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/WTF_NoHope"),
                InlineKeyboardButton("ᴇɴᴛᴇʀᴛᴀɪɴᴍᴇɴᴛ", callback_data="ent_vid")  # FIXED
            ],
            [InlineKeyboardButton("ʜᴇʟᴘ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs", callback_data='help')]
        ]

        photo_url = random.choice(PHOTO_URL)
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_url,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='markdown'
        )

    # ========================= GROUP ============================
    else:
        photo_url = random.choice(PHOTO_URL)

        keyboard = [
            [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f'http://t.me/{BOT_USERNAME}?startgroup=new')],
            [
                InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=f'https://t.me/{SUPPORT_CHAT}'),
                InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url=f'https://t.me/{UPDATE_CHAT}')
            ],
            [
                InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/WTF_NoHope"),
                InlineKeyboardButton("ᴇɴᴛᴇʀᴛᴀɪɴᴍᴇɴᴛ", callback_data="ent_vid")  # FIXED
            ],
            [InlineKeyboardButton("ʜᴇʟᴘ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs", callback_data='help')]
        ]

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_url,
            caption="🎴Alive!?...\nconnect to me in PM For more information",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# ===================================================
#                 CALLBACK HANDLER
# ===================================================
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    # -------- HELP ----------
    if query.data == 'help':
        help_text = """
    ***ʜᴇʟᴘ sᴇᴄᴛɪᴏɴ:***
    
***/guess: ᴛᴏ ɢᴜᴇss ᴄʜᴀʀᴀᴄᴛᴇʀ (ᴏɴʟʏ ɢʀᴏᴜᴘs)***
***/fav: ᴀᴅᴅ ʏᴏᴜʀ ғᴀᴠ***
***/trade : ᴛʀᴀᴅᴇ ᴄʜᴀʀᴀᴄᴛᴇʀs***
***/gift: ɢɪғᴛ ᴄʜᴀʀᴀᴄᴛᴇʀ ғʀᴏᴍ ʏᴏᴜʀ ᴄᴏʟʟᴇᴄᴛɪᴏɴ***
***/collection: sᴇᴇ ʏᴏᴜʀ ᴄᴏʟʟᴇᴄᴛɪᴏɴ***
***/topgroups : ᴛᴏᴘ ɢʀᴏᴜᴘ ʟɪsᴛ***
***/top: ᴛᴏᴘ ᴜsᴇʀs***
***/ctop : ʏᴏᴜʀ ᴄʜᴀᴛ ᴛᴏᴘ***
***/changetime: ᴄʜᴀɴɢᴇ ᴄʜᴀʀᴀᴄᴛᴇʀ ᴛɪᴍᴇ***
        """
        keyboard = [[InlineKeyboardButton("⤾ Bᴀᴄᴋ", callback_data='back')]]

        await query.edit_message_caption(
            caption=help_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='markdown'
        )

    # -------- BACK ----------
    elif query.data == 'back':

        caption = f"""
***ʜᴇʏʏʏʏ...***

***ɪ ᴀᴍ ɢʀᴀʙʙɪɴɢ ʏᴏᴜʀ ᴡᴀɪғᴜ ʙᴏᴛ... ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘs..!***
        """

        keyboard = [
            [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f'http://t.me/{BOT_USERNAME}?startgroup=new')],
            [
                InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=f'https://t.me/{SUPPORT_CHAT}'),
                InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url=f'https://t.me/{UPDATE_CHAT}')
            ],
            [
                InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/WTF_NoHope"),
                InlineKeyboardButton("ᴇɴᴛᴇʀᴛᴀɪɴᴍᴇɴᴛ", callback_data="ent_vid")
            ],
            [InlineKeyboardButton("ʜᴇʟᴘ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs", callback_data='help')]
        ]

        await query.edit_message_caption(
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='markdown'
        )


# PTB HANDLER REGISTRATION
application.add_handler(CallbackQueryHandler(button, pattern='^(help|back)$', block=False))
application.add_handler(CommandHandler("start", start, block=False))
