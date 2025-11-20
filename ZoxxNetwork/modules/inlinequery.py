import re
import time
from html import escape
from cachetools import TTLCache
from pymongo import ASCENDING

from telegram import Update, InlineQueryResultPhoto
from telegram.ext import InlineQueryHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from ZoxxNetwork import user_collection, collection, application, db


# Indexes
db.characters.create_index([('id', ASCENDING)])
db.characters.create_index([('anime', ASCENDING)])
db.characters.create_index([('img_url', ASCENDING)])

db.user_collection.create_index([('characters.id', ASCENDING)])
db.user_collection.create_index([('characters.name', ASCENDING)])
db.user_collection.create_index([('characters.img_url', ASCENDING)])

# Caches
all_characters_cache = TTLCache(maxsize=10000, ttl=36000)
user_collection_cache = TTLCache(maxsize=10000, ttl=60)



async def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0

    # -------------------------------
    # FIXED: Safe parsing for 'collection.<id>'
    # -------------------------------
    if query.startswith("collection."):
        parts = query.split(" ", 1)              # ["collection.<id>", "search terms..."]
        user_part = parts[0]                     # "collection.<id>"
        search_terms = parts[1] if len(parts) > 1 else ""

        if "." in user_part:
            user_id = user_part.split(".", 1)[1]
        else:
            user_id = None

        if user_id and user_id.isdigit():
            uid = int(user_id)

            # cached user
            if uid in user_collection_cache:
                user = user_collection_cache[uid]
            else:
                user = await user_collection.find_one({'id': uid})
                user_collection_cache[uid] = user

            if user:
                # remove duplicates
                all_characters = list({v['id']: v for v in user['characters']}.values())

                if search_terms:
                    regex = re.compile(search_terms, re.IGNORECASE)
                    all_characters = [c for c in all_characters if regex.search(c['name']) or regex.search(c['anime'])]
            else:
                all_characters = []

        else:
            all_characters = []

    else:
        # normal search
        if query:
            regex = re.compile(query, re.IGNORECASE)
            all_characters = list(
                await collection.find({
                    "$or": [{"name": regex}, {"anime": regex}]
                }).to_list(length=None)
            )
        else:
            # cache results
            if "all_characters" in all_characters_cache:
                all_characters = all_characters_cache["all_characters"]
            else:
                all_characters = list(await collection.find({}).to_list(length=None))
                all_characters_cache["all_characters"] = all_characters

    # Pagination
    characters = all_characters[offset:offset + 50]
    next_offset = str(offset + len(characters)) if len(characters) < 50 else str(offset + 50)

    # Build inline results
    results = []
    for character in characters:
        global_count = await user_collection.count_documents({'characters.id': character['id']})
        anime_characters = await collection.count_documents({'anime': character['anime']})

        if query.startswith("collection."):
            uid = int(user_id)
            user = user_collection_cache.get(uid)

            user_character_count = sum(c['id'] == character['id'] for c in user['characters'])
            user_anime_characters = sum(c['anime'] == character['anime'] for c in user['characters'])

            caption = (
                f"<b> Look At <a href='tg://user?id={user['id']}'>"
                f"{escape(user.get('first_name', user['id']))}</a>'s Character</b>\n\n"
                f"🌸: <b>{character['name']} (x{user_character_count})</b>\n"
                f"🏖️: <b>{character['anime']} ({user_anime_characters}/{anime_characters})</b>\n"
                f"<b>{character['rarity']}</b>\n\n"
                f"<b>🆔️:</b> {character['id']}"
            )
        else:
            caption = (
                f"<b>Look At This Character !!</b>\n\n"
                f"🌸:<b> {character['name']}</b>\n"
                f"🏖️: <b>{character['anime']}</b>\n"
                f"<b>{character['rarity']}</b>\n"
                f"🆔️: <b>{character['id']}</b>\n\n"
                f"<b>Globally Guessed {global_count} Times...</b>"
            )

        results.append(
            InlineQueryResultPhoto(
                id=f"{character['id']}_{time.time()}",
                photo_url=character['img_url'],
                thumbnail_url=character['img_url'],
                caption=caption,
                parse_mode='HTML'
            )
        )

    await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)



# Handler
application.add_handler(InlineQueryHandler(inlinequery, block=False))
