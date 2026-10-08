import os
import re
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

app = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()


async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.effective_user

    username = f"@{user.username}" if user.username else "нет username"
    name = user.full_name

    text = update.message.text or update.message.caption or "[медиа/файл]"

    message_to_admin = (
        f"👤 {name}\n"
        f"🔹 Username: {username}\n"
        f"🆔 ID: {user.id}\n\n"
        f"💬 Сообщение:\n{text}\n\n"
        f"↩️ Ответь на это сообщение, чтобы отправить ответ пользователю."
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=message_to_admin
    )


async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.reply_to_message:
        return

    if update.effective_user.id != ADMIN_ID:
        return

    replied_text = update.message.reply_to_message.text or ""

    match = re.search(r"🆔 ID: (\d+)", replied_text)

    if not match:
        await update.message.reply_text(
            "❌ Не удалось определить пользователя."
        )
        return

    user_id = int(match.group(1))

    await context.bot.send_message(
        chat_id=user_id,
        text=f"💬 Ответ администратора:\n\n{update.message.text}"
    )

    await update.message.reply_text("✅ Ответ отправлен.")


telegram_app.add_handler(
    MessageHandler(
        filters.ALL & ~filters.COMMAND,
                user_message
            )
)
