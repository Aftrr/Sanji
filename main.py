# main.py
# Sanji Telegram Bot — single-file ready for Render (includes imghdr fallback)
# Do not include BOT_TOKEN here. Put BOT_TOKEN in environment variables (.env locally or Render env vars).

import sys
# --- imghdr fallback for environments where stdlib imghdr is removed (e.g., Python 3.13) ---
_imghdr_code = r'''
def what(h, _=None):
    data = None
    try:
        # if given a filename (str), read a chunk from file
        if isinstance(h, str):
            with open(h, "rb") as f:
                data = f.read(32)
        else:
            data = h[:32]
    except Exception:
        return None

    if not data or len(data) < 10:
        return None

    # JPEG
    if data[0:3] == b"\xff\xd8\xff":
        return "jpeg"
    # PNG
    if data[0:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    # GIF
    if data[0:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    # TIFF
    if data[0:4] in (b"II*\x00", b"MM\x00*"):
        return "tiff"
    # BMP
    if data[0:2] == b"BM":
        return "bmp"
    # WEBP
    if data[0:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None
'''
if 'imghdr' not in sys.modules:
    import types
    mod = types.ModuleType('imghdr')
    exec(_imghdr_code, mod.__dict__)
    sys.modules['imghdr'] = mod
# --- end imghdr fallback ---

# normal imports
import logging
import os
import random
from dotenv import load_dotenv

# Telegram imports (python-telegram-bot v13.x)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Load environment (local .env or Render env vars)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN missing! Set BOT_TOKEN in environment variables.")

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Bot data ---
SANJI_QUOTES = [
    "A real chef never leaves anyone hungry.",
    "Cooking is love made visible.",
    "Don’t touch the ladies! Leave that to me.",
    "Food is the reason I breathe.",
    "A good meal heals a tired heart.",
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
    "For you, I'll cook a feast fit for the heavens.",
]

TOUGH_LINES = [
    "If you hurt my crew, you’re done. No second chances.",
    "Cooking and fighting both need perfect timing. Don’t test mine.",
]

SMALL_TALK = [
    "Hungry? I can suggest something! Use /cook to get a dish.",
    "A kitchen without respect is like a ship without a sail.",
    "Tell me a flavor and I’ll suggest a recipe!",
]

# --- Helpers ---
def pick_quote():
    return random.choice(SANJI_QUOTES)

def pick_dish():
    return random.choice(DISHES)

def sanji_reply_for_text(text: str) -> str:
    t = (text or "").lower()
    if any(word in t for word in ["cook", "dish", "food", "recipe", "khana"]):
        dish = pick_dish()
        return f"🍳 Try this: *{dish['name']}*\\n_{dish['desc']}_"
    if any(word in t for word in ["love", "beautiful", "crush", "pyar"]):
        return random.choice(FLIRTY_LINES)
    if any(word in t for word in ["fight", "enemy", "battle", "ladayi"]):
        return random.choice(TOUGH_LINES)
    return random.choice(SMALL_TALK)

# --- Handlers ---
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
    try:
        dish = pick_dish() if data == "dish:random" else DISHES[int(data.split(':')[1])]
    except Exception:
        dish = pick_dish()
    query.edit_message_text(f"🍽️ *{dish['name']}*\\n_{dish['desc']}_", parse_mode=ParseMode.MARKDOWN)

def echo_handler(update: Update, context: CallbackContext):
    text = update.message.text or ""
    update.message.reply_text(sanji_reply_for_text(text), parse_mode=ParseMode.MARKDOWN)

def error_handler(update: Update, context: CallbackContext):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# --- Main entry ---
def main():
    # Create Updater
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("quote", quote_cmd))
    dp.add_handler(CommandHandler("cook", cook_cmd))
    dp.add_handler(CommandHandler("menu", menu_cmd))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo_handler))
    dp.add_error_handler(error_handler)

    # Test connection & show bot info in logs (helps debug token issues)
    bot = updater.bot
    try:
        me = bot.get_me()
        logger.info("Logged in as: %s (id: %s)", getattr(me, "username", "unknown"), getattr(me, "id", "unknown"))
    except Exception as e:
        logger.exception("Failed to fetch bot info. Check BOT_TOKEN. Exception: %s", e)
        # If token invalid, don't attempt to start polling
        raise

    logger.info("Starting polling...")
    # Start polling (for Render use Background Worker or ensure process stays alive)
    updater.start_polling()
    logger.info("Polling started. Bot should respond to messages now.")
    updater.idle()

if __name__ == "__main__":
    main()
