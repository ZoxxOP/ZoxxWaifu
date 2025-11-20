from pyrogram import Client, filters

@Client.on_callback_query(filters.regex("entertainment_video"))
async def play_entertainment(_, query):
    await query.answer()
    await query.message.reply_video(
        video="https://files.catbox.moe/m5qcx3.mp4"
    )
