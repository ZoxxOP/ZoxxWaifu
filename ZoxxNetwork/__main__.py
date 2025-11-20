import importlib
import time
import random
import re
import asyncio
from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters

from ZoxxNetwork import (
    collection,
    top_global_groups_collection,
    group_user_totals_collection,
    user_collection,
    user_totals_collection,
    Waifuu,
    application,
    SUPPORT_CHAT,
    UPDATE_CHAT,
    db,
    LOGGER
)
from ZoxxNetwork.modules import ALL_MODULES


# Global Locks and Caches
locks = {}
message_counts = {}
last_user = {}
warned_users = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}


# -----------------------------
# Load all modules safely
# -----------------------------
for module_name in ALL_MODULES:
    try:
        importlib.import_module("ZoxxNetwork.modules." + module_name)
    except Exception as e:
        LOGGER.error(f"❌ Failed to load module: {module_name} → {e}")


# -----------------------------
# Helper
# -----------------------------
def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)


# -----------------------------
# Message Counter (Spam + Frequency)
# -----------------------------
async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()

    async with locks[chat_id]:

        # spam control
        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:

                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return

                await update.message.reply_text(
                    f"⚠️ Don't Spam {update.effective_user.first_name}...\n"
                    f"Your Messages Will be ignored for 10 Minutes..."
                )
                warned_users[user_id] = time.time()
                return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        # message frequency
        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        msg_freq = chat_frequency.get('message_frequency', 100) if chat_frequency else 100

        message_counts[chat_id] = message_counts.get(chat_id, 0) + 1

        if message_counts[chat_id] % msg_freq == 0:
            await send_image(update, context)
            message_counts[chat_id] = 0


# -----------------------------
# Send Character Image
# -----------------------------
async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    all_characters = list(await collection.find({}).to_list(length=None))

    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    # reset loop
    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    character = random.choice([c for c in all_characters if c['id'] not in sent_characters[chat_id]])

    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character

    first_correct_guesses.pop(chat_id, None)

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=character['img_url'],
        caption=f"A New {character['rarity']} Character Appeared...\n/guess Character Name and add in Your Harem",
        parse_mode='Markdown'
    )


# -----------------------------
# Guess Command
# -----------------------------
async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in last_characters:
        return

    if chat_id in first_correct_guesses:
        await update.message.reply_text('❌ Already Guessed By Someone.. Try Next Time!')
        return

    guess = ' '.join(context.args).lower() if context.args else ''

    if "()" in guess or "&" in guess.lower():
        await update.message.reply_text("❌ Invalid characters in guess.")
        return

    correct = last_characters[chat_id]
    name_parts = correct['name'].lower().split()

    if sorted(name_parts) == sorted(guess.split()) or any(part == guess for part in name_parts):
        first_correct_guesses[chat_id] = user_id

        user = await user_collection.find_one({'id': user_id})

        if user:
            update_fields = {}
            if update.effective_user.username != user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await user_collection.update_one({'id': user_id}, {'$set': update_fields})

            await user_collection.update_one({'id': user_id}, {'$push': {'characters': correct}})

        else:
            await user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'characters': [correct],
            })

        # group stats
        await update_group_stats(update, user_id, chat_id)

        # reply
        keyboard = [[InlineKeyboardButton("See Harem", switch_inline_query_current_chat=f"collection.{user_id}")]]
        msg = (
            f'<b><a href="tg://user?id={user_id}">{escape(update.effective_user.first_name)}</a></b> '
            f'You Guessed a New Character ✅\n\n'
            f'𝗡𝗔𝗠𝗘: <b>{correct["name"]}</b>\n'
            f'𝗔𝗡𝗜𝗠𝗘: <b>{correct["anime"]}</b>\n'
            f'𝗥𝗔𝗥𝗜𝗧𝗬: <b>{correct["rarity"]}</b>\n\n'
            f'This Character has been added to your harem!'
        )

        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

    else:
        await update.message.reply_text('❌ Incorrect name, try again!')


# -----------------------------
# Fav Command
# -----------------------------
async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text('Provide Character ID.')
        return

    character_id = context.args[0]
    user = await user_collection.find_one({'id': user_id})

    if not user:
        await update.message.reply_text('You have no characters yet.')
        return

    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        await update.message.reply_text('Character not in your collection.')
        return

    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': [character_id]}})
    await update.message.reply_text(f"{character['name']} added to favorites ❤️")


# -----------------------------
# Register Handlers & Run Bot
# -----------------------------
def main() -> None:
    application.add_handler(CommandHandler(["guess", "protecc", "collect", "grab", "hunt"], guess, block=False))
    application.add_handler(CommandHandler("fav", fav, block=False))
    application.add_handler(MessageHandler(filters.ALL, message_counter, block=False))

    application.run_polling(drop_pending_updates=True)


# -----------------------------
# Start
# -----------------------------
if __name__ == "__main__":
    Waifuu.start()
    LOGGER.info("Bot started successfully!")
    main()
