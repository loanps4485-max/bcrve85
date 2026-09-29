import json
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = 5379947962


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Bienvenue dans le magasin !\n\n"
        "Clique sur le bouton menu en bas pour ouvrir le magasin."
    )


async def handle_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.web_app_data:
        return

    try:
        data = json.loads(update.message.web_app_data.data)
    except Exception:
        await update.message.reply_text("Erreur lors de la lecture de la commande.")
        return

    await update.message.reply_text(
        f"✅ Commande reçue !\n\n"
        f"Total : {data.get('total', 0):.2f} €\n"
        f"Merci pour ton achat 🙌"
    )

    items_text = ""
    for item in data.get("items", []):
        items_text += (
            f"• {item['name']} x{item['quantity']} "
            f"= {item['subtotal']:.2f} €\n"
        )

    user = data.get("user") or {}
    user_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
    username = f"@{user.get('username')}" if user.get("username") else "Pas de username"
    user_id = user.get("id", "Inconnu")

    admin_message = (
        f"🛒 **Nouvelle commande**\n\n"
        f"👤 Client : {user_name}\n"
        f"🔗 {username}\n"
        f"🆔 ID : `{user_id}`\n\n"
        f"📦 Articles :\n{items_text}\n"
        f"💰 **Total : {data.get('total', 0):.2f} €**"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode="Markdown",
        )
    except Exception as error:
        print("Erreur envoi admin:", error)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp)
    )

    print("Bot démarré...")
    app.run_polling()


if __name__ == "__main__":
    main()