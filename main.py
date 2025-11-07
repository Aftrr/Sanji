import logging
import os
import random
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Load token from .env file
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing! Create .env file with BOT_TOKEN=your_token_here")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

SANJI_QUOTES = [
    "A real chef never leaves anyone hungry.",
    "Cooking is love made visible.",
    "Food is the reason I breathe.",
    "Don’t touch the ladies! Leave that to me.",
    "A good meal heals a tired heart."
]

DISHES = [
    {"name": "Sea Breeze Pasta", "desc": "Pasta with garlic, shrimp, and lemon zest."},
    {"name": "Black Leg Curry", "desc": "Spicy curry with braised beef (or tofu)."},
    {"name": "Sanji’s Special Omelette", "desc": "Fluffy omelette with herbs and cheese."},
    {"name": "Comfort Ramen", "desc": "Rich broth with noodles, egg, and scallions."},
    {"name": "Herb Grilled Fish", "desc": "Whole fish grilled with citrus-herb butter."},
]

FLIRTY_LINES = [
    "Ah, such beauty! You must be the reason the sea sparkles today. 😏",
    "If you were a dish, you'd be the chef's masterpiece.",
    "For you, I'll cook a feast fit for the heavens."
]

TOUGH_LINES = [
    "If you hurt my crew, you’re done. No second chances.",
    "Cooking and fighting both need perfect timing. Don’t test mine."
]

SMALL_TALK = [
    "Hungry? I can suggest something! Use /cook to get a dish.",
    "A kitchen without respect is like a ship without a sail.",
    "Tell me a flavor and I’ll suggest a recipe!"
]

def pick_quote():
    return random.choice(SANJI_QUOTES)

def pick_dish():
    return random.choice(DISHES)

def sanji_reply(text: str) -> str:
    t = text.lower()
    if any(word in t for word in ["cook", "dish", "food", "recipe", "khana"]):
        dish = pick_dish()
        return f"🍳 Try this: *{dish['name']}*\\n_{dish['desc']}_"
    if any(word in t for word in ["love", "beautiful", "crush", "pyar"]):
        return random.choice(FLIRTY_LINES)
    if any(word in t for word in ["fight", "enemy", "battle", "ladayi"]):
        return random.choice(TOUGH_LINES)
    return random.choice(SMALL_TALK)

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    msg = (
        f"🔥 *Welcome aboard, {user.first_name}!*\\n"
        "I'm Sanji, the Straw Hat cook. Hungry? Type /cook or /menu.\\n"
        "Need help? Use /help."
    )
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

def help_cmd(update: Update, context: CallbackContext):
    msg = (
        "*Commands:*\\n"
        "/start — Welcome\\n"
        "/help — Show help\\n"
        "/quote — Random Sanji quote\\n"
        "/cook — Random dish\\n"
        "/menu — Interactive food menu"
    )
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

def quote_cmd(update: Update, context: CallbackContext):
    update.message.reply_text(f'\"{pick_quote()}\" — *Sanji*', parse_mode=ParseMode.MARKDOWN)

def cook_cmd(update: Update, context: CallbackContext):
    dish = pick_dish()
    text = f"🍛 *{dish['name']}*\\n_{dish['desc']}_\\n\\n✨ Tip: Add garlic and lemon for extra flavor!"
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

def menu_cmd(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton(d['name'], callback_data=f"dish:{i}")] for i, d in enumerate(DISHES)]
    keyboard.append([InlineKeyboardButton("🎲 Surprise me!", callback_data="dish:random")])
    update.message.reply_text("Here’s the menu — pick a dish:", reply_markup=InlineKeyboardMarkup(keyboard))

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    dish = pick_dish() if data == "dish:random" else DISHES[int(data.split(':')[1])]
    query.edit_message_text(f"🍽️ *{dish['name']}*\\n_{dish['desc']}_", parse_mode=ParseMode.MARKDOWN)

def echo_handler(update: Update, context: CallbackContext):
    text = update.message.text or ""
    update.message.reply_text(sanji_reply(text), parse_mode=ParseMode.MARKDOWN)

def error_handler(update: Update, context: CallbackContext):
    logger.error(msg="Error occurred:", exc_info=context.error)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("quote", quote_cmd))
    dp.add_handler(CommandHandler("cook", cook_cmd))
    dp.add_handler(CommandHandler("menu", menu_cmd))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo_handler))
    dp.add_error_handler(error_handler)
    updater.start_polling()
    logger.info("Sanji Bot started 🍳")
    updater.idle()

if __name__ == "__main__":
    main()
