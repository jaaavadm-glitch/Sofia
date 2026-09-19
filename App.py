لطفا به دکمه ها و رنگ هاشون هیچ دستی نزن فقط دکمه های جدید رنگ هم بزن بهشون همون منوی پایین 
رو میگم اونام باید رنگ داشته باشن
import logging
import json
import urllib.parse
import time
import asyncio
import os
import uuid as uuidlib
import secrets
import requests as req
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ================== تنظیمات ==================
BOT_TOKEN = "8516592763:AAGH6b_IaENH_ZRi6ZP1LKmwb3aDk8NvGcU"
ADMIN_ID = 8950697733
REQUIRED_CHANNEL = "@vexo_officia1"
CHANNEL_LINK = "https://t.me/vexo_officia1"
CARD_NUMBER = "6219861355256818"

PANEL_URL = "https://vexo-panel-8950697733-c9914a.jaaavadm.workers.dev"
PANEL_HOST = "vexo-panel-8950697733-c9914a.jaaavadm.workers.dev"
PANEL_PASS = "JU6TpgcCKjxd"

STAR_PRICE_TOMAN = 400
PREMIUM_3M = 1200000
PREMIUM_6M = 1800000
PREMIUM_12M = 2800000
PREMIUM_STAR_COST = {3: 1000, 6: 1500, 12: 2500}

CONFIG_PLANS = [
    {"label": "۱ گیگابایت", "gb": 1, "days": 30, "price": 5000,  "emoji": "🔹"},
    {"label": "۳ گیگابایت", "gb": 3, "days": 30, "price": 15000, "emoji": "🔸"},
    {"label": "۵ گیگابایت", "gb": 5, "days": 30, "price": 35000, "emoji": "🔹"},
    {"label": "۷ گیگابایت", "gb": 7, "days": 30, "price": 50000, "emoji": "🔸"},
    {"label": "۸ گیگابایت", "gb": 8, "days": 30, "price": 65000, "emoji": "🔹"},
]

STAR_PACKAGES = [
    {"count": 50,   "label": "۵۰ استارز",   "emoji": "🔹"},
    {"count": 100,  "label": "۱۰۰ استارز",  "emoji": "🔸"},
    {"count": 250,  "label": "۲۵۰ استارز",  "emoji": "🔹"},
    {"count": 500,  "label": "۵۰۰ استارز",  "emoji": "🔸"},
    {"count": 1000, "label": "۱۰۰۰ استارز", "emoji": "🔹"},
    {"count": 2500, "label": "۲۵۰۰ استارز", "emoji": "🔸"},
]

(ASK_USERNAME, ASK_PASSWORD, ASK_CONFIRM) = range(3)
(CHANGE_PASS_OLD, CHANGE_PASS_NEW, CHANGE_PASS_CONFIRM) = range(10, 13)
(CHANGE_NAME_NEW,) = range(20, 21)

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO)
logger = logging.getLogger("VEXO-BOT")

# ================== دیتابیس ==================
DB_FILE = "users_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

users_db = load_db()

def format_price(price):
    return f"{price:,} تومان"

def to_english_digits(s):
    return s.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))

# ================== 🔥 توابع HTTP API ==================
def send_msg(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        return req.post(url, json=payload, timeout=15).json()
    except Exception as e:
        logger.error(f"send_msg error: {e}")
        return {"ok": False}

def send_inline(chat_id, text, buttons=None, parse_mode="Markdown"):
    rm = {"inline_keyboard": buttons} if buttons else None
    return send_msg(chat_id, text, reply_markup=rm, parse_mode=parse_mode)

def edit_inline(chat_id, message_id, text, buttons=None, parse_mode="Markdown"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode}
    if buttons is not None:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    try:
        return req.post(url, json=payload, timeout=15).json()
    except Exception as e:
        logger.error(f"edit_inline error: {e}")
        return {"ok": False}

# ================== 🎨 کیبورد پایین رنگی ==================
def send_reply_keyboard(chat_id, text):
    keyboard = {
        "keyboard": [
            [{"text": "👤 حساب کاربر", "style": "primary"}],
            [
                {"text": "🛒 خرید کانفیگ", "style": "success"},
                {"text": "💎 خرید پرمیوم", "style": "success"}
            ],
            [
                {"text": "⭐ استارز تلگرام", "style": "danger"},
                {"text": "🎫 تیکت پشتیبانی", "style": "primary"}
            ],
            [
                {"text": "💰 موجودی من", "style": "success"},
                {"text": "🌐 سایت‌های ما", "style": "primary"}
            ],
        ],
        "resize_keyboard": True,
        "is_persistent": True,
        "input_field_placeholder": "یکی از گزینه‌ها رو انتخاب کن..."
    }
    return send_msg(chat_id, text, reply_markup=keyboard)

# ================== پنل VEXO ==================
def panel_create_user(name, gb, days):
    try:
        # 🔥 استفاده از API جدید (بدون کوکی)
        r = req.post(
            f"{PANEL_URL}/api/bot/create-user",
            json={"name": name, "gb": gb, "days": days},
            headers={"X-API-Key": PANEL_PASS},
            timeout=15
        )
        data = r.json()
        if data.get("ok"):
            return {"ok": True, "uuid": data["uuid"]}
        return {"ok": False, "error": data.get("error", "خطا")}
    except Exception as e:
        return {"ok": False, "error": str(e)}
def build_vless_config(uuid, name):
    return (
        f"vless://{uuid}@{PANEL_HOST}:443"
        f"?encryption=none&security=tls&sni={PANEL_HOST}"
        f"&fp=chrome&type=ws&host={PANEL_HOST}"
        f"&path=%2F%3Fed%3D2048#{urllib.parse.quote(name)}"
    )

def build_sub_link(uuid):
    return f"{PANEL_URL}/sub/{uuid}"

# ================== دکمه‌های شیشه‌ای ==================
def back_button():
    return [{"text": "🔙  بــازگــشــت", "callback_data": "back_main", "style": "danger"}]

def main_menu_buttons():
    return [
        [{"text": "👤  حــســاب کــاربر", "callback_data": "account", "style": "primary"}],
        [{"text": "🛒  خــریــد کــانــفــیــگ", "callback_data": "panel", "style": "success"}],
        [{"text": "💎  خــریــد پــرمــیــوم", "callback_data": "premium", "style": "success"}],
        [{"text": "⭐  اســتــارز تــلــگــرام", "callback_data": "stars", "style": "danger"}],
        [{"text": "🎫  تــیــکــت پــشــتــیــبــانــی", "callback_data": "ticket", "style": "primary"}],
        [{"text": "🌐  ســایــت‌هــای مــا", "callback_data": "sites", "style": "primary"}],
    ]

def sites_buttons():
    return [
        [{"text": "🟣  V E X O O", "url": "https://vexoo.gt.tc", "style": "success"}],
        [{"text": "🔵  V E X A Y", "url": "https://vexay.gt.tc", "style": "primary"}],
        [{"text": "🟢  S A F I O", "url": "https://safio.gt.tc", "style": "success"}],
        [{"text": "🟠  S A V E I T", "url": "https://saveit.gt.tc", "style": "danger"}],
        back_button(),
    ]

def account_buttons():
    return [
        [{"text": "✏️  تــغــیــیــر نــام", "callback_data": "change_name", "style": "primary"}],
        [{"text": "🔑  تــغــیــیــر رمــز", "callback_data": "change_pass", "style": "primary"}],
        [{"text": "🛒  ســفــارشــات مــن", "callback_data": "my_orders", "style": "primary"}],
        back_button(),
    ]

def payment_buttons(order_type, order_id):
    return [
        [{"text": "📸  ارســال رســیــد پــرداخــت", "callback_data": f"send_receipt_{order_type}_{order_id}", "style": "success"}],
        back_button(),
    ]

# ================== چک عضویت ==================
async def is_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# ================== /start ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "دوست عزیز"

    if not await is_member(context, user.id):
        send_inline(
            chat_id=user.id,
            text=f"سلام {name} جان 👋\n\nخوش اومدی!\n\nاول عضو کانال شو:",
            buttons=[
                [{"text": "📢  عــضــویــت در کــانــال", "url": CHANNEL_LINK, "style": "primary"}],
                [{"text": "✅  عــضــو شــدم", "callback_data": "check_membership", "style": "success"}],
            ]
        )
        return ConversationHandler.END

    if str(user.id) in users_db and users_db[str(user.id)].get("registered"):
        send_reply_keyboard(user.id, f"خوش برگشتی {name} جان 🌹\n\nاز منوی زیر انتخاب کن:")
        return ConversationHandler.END

    await update.message.reply_text(
        f"خوش اومدی {name} جان 🎉\n\nیه **نام کاربری** برای خودت انتخاب کن:",
        parse_mode="Markdown"
    )
    return ASK_USERNAME

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if await is_member(context, query.from_user.id):
        try:
            await query.message.delete()
        except Exception:
            pass
        send_reply_keyboard(query.from_user.id, "✅ عضویتت تایید شد!\n\nاز منوی زیر انتخاب کن:")
    else:
        await query.answer("هنوز عضو نشدی! 😅", show_alert=True)

# ================== ثبت‌نام ==================
async def ask_username(update, context):
    username = update.message.text.strip()
    if len(username) < 3:
        await update.message.reply_text("حداقل ۳ حرف:")
        return ASK_USERNAME
    context.user_data["temp_username"] = username
    await update.message.reply_text("عالیه ✨\n\nحالا یه **رمز** بذار:\n(حداقل ۴ کاراکتر)", parse_mode="Markdown")
    return ASK_PASSWORD

async def ask_password(update, context):
    password = update.message.text.strip()
    if len(password) < 4:
        await update.message.reply_text("حداقل ۴ کاراکتر:")
        return ASK_PASSWORD
    context.user_data["temp_password"] = password
    await update.message.reply_text("🔐 تکرار رمز:")
    return ASK_CONFIRM

async def ask_confirm(update, context):
    confirm = update.message.text.strip()
    if confirm != context.user_data.get("temp_password"):
        await update.message.reply_text("❌ یکی نیستن! /start")
        return ConversationHandler.END
    user_id = str(update.effective_user.id)
    users_db[user_id] = {
        "username": context.user_data.get("temp_username"),
        "password": context.user_data.get("temp_password"),
        "registered": True, "premium": False, "premium_until": None, "stars": 0,
        "panels": [], "orders": [], "joined_at": int(time.time()),
        "first_name": update.effective_user.first_name,
        "tg_username": update.effective_user.username or ""
    }
    save_db(users_db)
    context.user_data.pop("temp_username", None)
    context.user_data.pop("temp_password", None)
    send_reply_keyboard(update.effective_chat.id, "✅ حسابت ساخته شد!\n\nاز منوی زیر انتخاب کن:")
    return ConversationHandler.END

# ================== تغییر رمز/نام ==================
async def change_pass_old(update, context):
    if update.message.text.strip() != users_db.get(str(update.effective_user.id), {}).get("password", ""):
        await update.message.reply_text("❌ رمز اشتباهه! /cancel")
        return CHANGE_PASS_OLD
    await update.message.reply_text("✅ رمز جدید:")
    return CHANGE_PASS_NEW

async def change_pass_new(update, context):
    np = update.message.text.strip()
    if len(np) < 4:
        await update.message.reply_text("حداقل ۴ کاراکتر:")
        return CHANGE_PASS_NEW
    context.user_data["new_pass"] = np
    await update.message.reply_text("🔐 تکرار:")
    return CHANGE_PASS_CONFIRM

async def change_pass_confirm(update, context):
    if update.message.text.strip() != context.user_data.get("new_pass"):
        await update.message.reply_text("❌ یکی نیستن!")
        return ConversationHandler.END
    user_id = str(update.effective_user.id)
    users_db[user_id]["password"] = context.user_data.get("new_pass")
    save_db(users_db)
    context.user_data.pop("new_pass", None)
    await update.message.reply_text("✅ رمز تغییر کرد!")
    send_reply_keyboard(update.effective_chat.id, "🏠 منوی اصلی:")
    return ConversationHandler.END

async def change_name_new(update, context):
    nn = update.message.text.strip()
    if len(nn) < 3:
        await update.message.reply_text("حداقل ۳ کاراکتر:")
        return CHANGE_NAME_NEW
    user_id = str(update.effective_user.id)
    users_db[user_id]["username"] = nn
    save_db(users_db)
    await update.message.reply_text(f"✅ نام به «{nn}» تغییر کرد!")
    send_reply_keyboard(update.effective_chat.id, "🏠 منوی اصلی:")
    return ConversationHandler.END

async def cancel(update, context):
    for k in ["pending_approval", "awaiting_receipt", "awaiting_ticket", "changing_name", "changing_pass"]:
        context.user_data.pop(k, None)
    send_reply_keyboard(update.effective_chat.id, "لغو شد.\n\n🏠 منوی اصلی:")
    return ConversationHandler.END

# ================== هندلر دکمه‌های شیشه‌ای ==================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    user_id = str(query.from_user.id)
    user = users_db.get(user_id, {})

    if data == "back_main":
        edit_inline(chat_id, message_id, "🏠 **منوی اصلی:**", buttons=main_menu_buttons())

    elif data == "account":
        ps = "✅ فعال" if user.get("premium") else "❌ غیرفعال"
        joined = time.strftime("%Y-%m-%d", time.localtime(user.get("joined_at", 0)))
        text = (
            f"👤 **حساب کاربری شما**\n\n"
            f"🆔 `{user_id}`\n📛 {query.from_user.first_name}\n"
            f"🔗 @{query.from_user.username or 'نداری'}\n\n"
            f"👤 **نام کاربری:** `{user.get('username', '-')}`\n"
            f"🔒 **رمز:** `{user.get('password', '-')}`\n"
            f"📅 **عضویت:** {joined}\n\n"
            f"💎 **پرمیوم:** {ps}\n"
            f"⭐ **استارز:** {user.get('stars', 0)}\n"
            f"🛒 **سفارشات:** {len(user.get('orders', []))}"
        )
        edit_inline(chat_id, message_id, text, buttons=account_buttons())

    elif data == "change_name":
        edit_inline(chat_id, message_id, "✏️ **تغییر نام**\n\nنام جدید رو بفرست.\n\n/cancel برای لغو")
        context.user_data["changing_name"] = True

    elif data == "change_pass":
        edit_inline(chat_id, message_id, "🔑 **تغییر رمز**\n\nرمز فعلی رو وارد کن.\n\n/cancel برای لغو")
        context.user_data["changing_pass"] = True

    elif data == "my_orders":
        orders = user.get("orders", [])
        if not orders:
            edit_inline(chat_id, message_id, "🛒 **سفارشات**\n\nهنوز سفارشی نداری.", buttons=[back_button()])
        else:
            txt = "🛒 **سفارشات من**\n\n"
            for i, o in enumerate(orders[-10:], 1):
                e = "✅" if o['status'] == "تایید شده" else "⏳" if "انتظار" in o['status'] else "❌"
                txt += f"{i}. {o['type']} — {e} {o['status']}\n"
            edit_inline(chat_id, message_id, txt, buttons=[back_button()])

    elif data == "panel":
        text = "🔰 **سرویس کانفیگ V2Ray** 🔰\n\n✨ اینترنت پرسرعت و پایدار ✨\n\n📦 **تعرفه‌ها:**\n\n"
        buttons = []
        for i, plan in enumerate(CONFIG_PLANS):
            text += f"{plan['emoji']} {plan['label']} ➖ {format_price(plan['price'])}\n"
            buttons.append([{
                "text": f"{plan['emoji']}  {plan['label']}  |  {format_price(plan['price'])}",
                "callback_data": f"buy_config_{i}",
                "style": "success"
            }])
        text += "\n🚀 همین حالا سفارش دهید!"
        buttons.append(back_button())
        edit_inline(chat_id, message_id, text, buttons=buttons)

    elif data.startswith("buy_config_"):
        idx = int(data.replace("buy_config_", ""))
        plan = CONFIG_PLANS[idx]
        order_id = uuidlib.uuid4().hex[:8]
        users_db.setdefault(user_id, {}).setdefault("orders", []).append({
            "type": f"کانفیگ {plan['label']}", "status": "در انتظار پرداخت",
            "order_id": order_id, "price": plan['price'],
            "gb": plan['gb'], "days": plan['days'], "time": int(time.time())
        })
        save_db(users_db)
        text = (
            f"🛒 **سفارش {plan['label']}**\n\n"
            f"📦 {plan['label']} | ⏱ {plan['days']} روز\n"
            f"💰 **{format_price(plan['price'])}**\n\n"
            f"💳 **شماره کارت:**\n`{CARD_NUMBER}`\n\n"
            f"📸 بعد از واریز، عکس رسید رو بفرست.\n\n"
            f"🔖 سفارش: `{order_id}`"
        )
        edit_inline(chat_id, message_id, text, buttons=payment_buttons("config", order_id))

    elif data.startswith("send_receipt_config_"):
        oid = data.replace("send_receipt_config_", "")
        context.user_data["awaiting_receipt"] = {"type": "config", "order_id": oid}
        edit_inline(chat_id, message_id, "📸 **ارسـال رسـیـد**\n\nعکس رسید رو بفرست.", buttons=[back_button()])

    elif data == "premium":
        text = (
            "💎 **خرید پرمیوم تلگرام**\n\n"
            f"🟢 ۳ ماهه → {format_price(PREMIUM_3M)}\n"
            f"🟡 ۶ ماهه → {format_price(PREMIUM_6M)}\n"
            f"🟠 ۱۲ ماهه → {format_price(PREMIUM_12M)}"
        )
        buttons = [
            [{"text": f"🟢  ۳ مــاهــه | {format_price(PREMIUM_3M)}", "callback_data": "buy_premium_3", "style": "success"}],
            [{"text": f"🟡  ۶ مــاهــه | {format_price(PREMIUM_6M)}", "callback_data": "buy_premium_6", "style": "success"}],
            [{"text": f"🟠  ۱۲ مــاهــه | {format_price(PREMIUM_12M)}", "callback_data": "buy_premium_12", "style": "success"}],
            back_button(),
        ]
        edit_inline(chat_id, message_id, text, buttons=buttons)

    elif data.startswith("buy_premium_"):
        months = int(data.replace("buy_premium_", ""))
        price = {3: PREMIUM_3M, 6: PREMIUM_6M, 12: PREMIUM_12M}[months]
        order_id = uuidlib.uuid4().hex[:8]
        users_db.setdefault(user_id, {}).setdefault("orders", []).append({
            "type": f"پرمیوم {months} ماهه", "status": "در انتظار پرداخت",
            "order_id": order_id, "price": price, "time": int(time.time())
        })
        save_db(users_db)
        text = (
            f"💎 **پرمیوم {months} ماهه**\n\n"
            f"💰 **{format_price(price)}**\n\n"
            f"💳 **شماره کارت:**\n`{CARD_NUMBER}`\n\n"
            f"📸 عکس رسید رو بفرست.\n\n"
            f"🔖 سفارش: `{order_id}`"
        )
        edit_inline(chat_id, message_id, text, buttons=payment_buttons("premium", order_id))

    elif data.startswith("send_receipt_premium_"):
        oid = data.replace("send_receipt_premium_", "")
        context.user_data["awaiting_receipt"] = {"type": "premium", "order_id": oid}
        edit_inline(chat_id, message_id, "📸 **ارسـال رسـیـد**\n\nعکس رو بفرست.", buttons=[back_button()])

    elif data == "stars":
        text = "⭐ **استارز تلگرام**\n\n" + f"💵 هر استارز: {format_price(STAR_PRICE_TOMAN)}\n\n📦 **بسته‌ها:**\n"
        buttons = []
        for pkg in STAR_PACKAGES:
            total = pkg["count"] * STAR_PRICE_TOMAN
            text += f"{pkg['emoji']} {pkg['label']} → {format_price(total)}\n"
            buttons.append([{
                "text": f"{pkg['emoji']}  {pkg['label']}  |  {format_price(total)}",
                "callback_data": f"buy_stars_{pkg['count']}",
                "style": "success"
            }])
        buttons.append(back_button())
        edit_inline(chat_id, message_id, text, buttons=buttons)

    elif data.startswith("buy_stars_"):
        count = int(data.replace("buy_stars_", ""))
        total = count * STAR_PRICE_TOMAN
        order_id = uuidlib.uuid4().hex[:8]
        users_db.setdefault(user_id, {}).setdefault("orders", []).append({
            "type": f"{count} استارز", "status": "در انتظار پرداخت",
            "order_id": order_id, "price": total, "time": int(time.time())
        })
        save_db(users_db)
        text = (
            f"⭐ **{count} استارز**\n\n"
            f"💰 **{format_price(total)}**\n\n"
            f"💳 **شماره کارت:**\n`{CARD_NUMBER}`\n\n"
            f"📸 عکس رسید رو بفرست.\n\n"
            f"🔖 سفارش: `{order_id}`"
        )
        edit_inline(chat_id, message_id, text, buttons=payment_buttons("stars", order_id))

    elif data.startswith("send_receipt_stars_"):
        oid = data.replace("send_receipt_stars_", "")
        context.user_data["awaiting_receipt"] = {"type": "stars", "order_id": oid}
        edit_inline(chat_id, message_id, "📸 **ارسـال رسـیـد**\n\nعکس رو بفرست.", buttons=[back_button()])

    elif data == "ticket":
        edit_inline(chat_id, message_id, "🎫 **تیکت پشتیبانی**\n\nپیامت رو بفرست، به ادمین میره.\n\n/cancel برای لغو")
        context.user_data["awaiting_ticket"] = True

    elif data == "sites":
        edit_inline(chat_id, message_id, "🌐 **سایت‌های ما**", buttons=sites_buttons())

    # ================== ادمین ==================
    elif data.startswith("admin_approve_"):
        if query.from_user.id != ADMIN_ID:
            return
        parts = data.replace("admin_approve_", "").split("_")
        order_id, buyer_id = parts[0], parts[1]

        buyer = users_db.get(buyer_id, {})
        target_order = None
        for o in buyer.get("orders", []):
            if o.get("order_id") == order_id:
                target_order = o
                break
        if not target_order:
            await query.answer("سفارش پیدا نشد!", show_alert=True)
            return

        order_type = target_order.get("type", "")

        # پرمیوم
        if "پرمیوم" in order_type:
            try:
                months = int(to_english_digits(order_type.split()[1].replace("ماهه", "")))
            except Exception:
                months = 3
            star_cost = PREMIUM_STAR_COST.get(months, 1000)
            try:
                r = req.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/giftPremiumSubscription",
                    json={"user_id": int(buyer_id), "month_count": months, "star_count": star_cost,
                          "text": f"🎁 پرمیوم {months} ماهه از VEXO"},
                    timeout=30
                )
                result = r.json()
                if result.get("ok"):
                    users_db[buyer_id]["premium"] = True
                    target_order["status"] = "تایید شده"
                    save_db(users_db)
                    send_inline(ADMIN_ID, f"✅ `{order_id}` تایید و پرمیوم فعال شد.")
                    send_inline(int(buyer_id), f"🎉 **تایید شد!**\n\n💎 پرمیوم {months} ماهه فعال شد ❤️")
                    return
                else:
                    send_inline(ADMIN_ID, f"❌ خطا: `{result.get('description')}`")
                    return
            except Exception as e:
                send_inline(ADMIN_ID, f"❌ خطای شبکه: `{e}`")
                return

        # استارز
        if "استارز" in order_type:
            try:
                count = int(to_english_digits(order_type.split()[0]))
            except Exception:
                count = 0
            if count > 0:
                users_db[buyer_id]["stars"] = users_db[buyer_id].get("stars", 0) + count
                target_order["status"] = "تایید شده"
                save_db(users_db)
                send_inline(ADMIN_ID, f"✅ `{order_id}` تایید شد. ⭐ {count} استارز اضافه شد.")
                send_inline(int(buyer_id), f"🎉 **تایید شد!**\n\n⭐ {count} استارز اضافه شد.\n💰 موجودی: `{users_db[buyer_id]['stars']}`")
                return

        # کانفیگ - خودکار!
        if "کانفیگ" in order_type:
            panel_user_name = f"user_{buyer_id[-4:]}"
            gb = target_order.get("gb", 1)
            days = target_order.get("days", 30)
            send_inline(ADMIN_ID, f"⏳ در حال ساخت کاربر در پنل...\n👤 `{panel_user_name}` | {gb} گیگ | {days} روز")

            result = panel_create_user(panel_user_name, gb, days)
            if not result["ok"]:
                send_inline(ADMIN_ID, f"❌ خطا در پنل: `{result['error']}`")
                return

            new_uuid = result["uuid"]
            config = build_vless_config(new_uuid, panel_user_name)
            sub_link = build_sub_link(new_uuid)

            target_order["status"] = "تایید شده"
            target_order["uuid"] = new_uuid
            target_order["config"] = config
            target_order["panel_user"] = panel_user_name
            save_db(users_db)

            send_inline(ADMIN_ID, f"✅ `{order_id}` تایید و کاربر خودکار ساخته شد!\n🆔 `{new_uuid}`")

            user_msg = (
                f"🎉 **پرداخت تایید شد!**\n\n"
                f"📦 **{order_type}**\n"
                f"🔖 `{order_id}`\n\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🔗 **کانفیگ شما:**\n`{config}`\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"📱 **لینک اشتراک:**\n`{sub_link}`\n\n"
                f"💡 کانفیگ رو کپی کن و توی اپ v2rayNG وارد کن."
            )
            send_inline(int(buyer_id), user_msg)
            return

        # سایر
        context.user_data["pending_approval"] = {"order_id": order_id, "buyer_id": buyer_id}
        send_inline(ADMIN_ID, f"✍️ اطلاعات تحویل برای `{order_id}`:\n\n`-` بنویس اگه نیازی نیست.")

    elif data.startswith("admin_reject_"):
        if query.from_user.id != ADMIN_ID:
            return
        parts = data.replace("admin_reject_", "").split("_")
        order_id, buyer_id = parts[0], parts[1]
        u = users_db.get(buyer_id, {})
        for o in u.get("orders", []):
            if o.get("order_id") == order_id:
                o["status"] = "رد شده"
                break
        save_db(users_db)
        send_inline(ADMIN_ID, f"❌ `{order_id}` رد شد.")
        send_inline(int(buyer_id), f"❌ **رسید تایید نشد.**\n\n🔖 `{order_id}`")

# ================== دریافت عکس رسید ==================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    awaiting = context.user_data.get("awaiting_receipt")
    if not awaiting:
        return
    context.user_data.pop("awaiting_receipt", None)

    order_id = awaiting["order_id"]
    order_type = awaiting["type"]

    caption = f"📸 رسید جدید\n👤 {update.effective_user.first_name}\n🆔 `{user_id}`\n📦 {order_type}\n🔖 `{order_id}`"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": ADMIN_ID,
        "photo": update.message.photo[-1].file_id,
        "caption": caption,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "✅ تایید", "callback_data": f"admin_approve_{order_id}_{user_id}", "style": "success"}],
                [{"text": "❌ رد", "callback_data": f"admin_reject_{order_id}_{user_id}", "style": "danger"}],
            ]
        }
    }
    try:
        r = req.post(url, json=payload, timeout=15).json()
        if r.get("ok"):
            send_reply_keyboard(update.effective_chat.id, "✅ رسیدت برای ادمین ارسال شد.")
        else:
            send_msg(update.effective_chat.id, f"❌ خطا: `{r.get('description')}`")
    except Exception as e:
        send_msg(update.effective_chat.id, f"❌ خطای شبکه: `{str(e)[:100]}`")

# ================== پیام‌های متنی ==================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    user_id = str(update.effective_user.id)

    # ==========================================
    # 🔥 اول دکمه‌های پایین (Reply Keyboard)
    # ==========================================
    reply_buttons = {
        "👤 حساب کاربر": "account",
        "🛒 خرید کانفیگ": "panel",
        "💎 خرید پرمیوم": "premium",
        "⭐ استارز تلگرام": "stars",
        "🎫 تیکت پشتیبانی": "ticket",
        "💰 موجودی من": "balance",
        "🌐 سایت‌های ما": "sites",
    }

    if text in reply_buttons:
        action = reply_buttons[text]
        user = users_db.get(user_id, {})

        if action == "account":
            ps = "✅ فعال" if user.get("premium") else "❌ غیرفعال"
            joined = time.strftime("%Y-%m-%d", time.localtime(user.get("joined_at", 0)))
            send_inline(
                update.effective_chat.id,
                f"👤 **حساب کاربری شما**\n\n"
                f"🆔 `{user_id}`\n📛 {update.effective_user.first_name}\n"
                f"🔗 @{update.effective_user.username or 'نداری'}\n\n"
                f"👤 **نام کاربری:** `{user.get('username', '-')}`\n"
                f"🔒 **رمز:** `{user.get('password', '-')}`\n"
                f"📅 **عضویت:** {joined}\n\n"
                f"💎 **پرمیوم:** {ps}\n"
                f"⭐ **استارز:** `{user.get('stars', 0)}`\n"
                f"🛒 **سفارشات:** {len(user.get('orders', []))}",
                buttons=account_buttons()
            )

        elif action == "panel":
            text2 = "🔰 **سرویس کانفیگ V2Ray** 🔰\n\n✨ اینترنت پرسرعت و پایدار ✨\n\n📦 **تعرفه‌ها:**\n\n"
            buttons = []
            for i, plan in enumerate(CONFIG_PLANS):
                text2 += f"{plan['emoji']} {plan['label']} ➖ {format_price(plan['price'])}\n"
                buttons.append([{
                    "text": f"{plan['emoji']}  {plan['label']}  |  {format_price(plan['price'])}",
                    "callback_data": f"buy_config_{i}",
                    "style": "success"
                }])
            text2 += "\n🚀 همین حالا سفارش دهید!"
            send_inline(update.effective_chat.id, text2, buttons=buttons)

        elif action == "premium":
            text2 = (
                "💎 **خرید پرمیوم تلگرام**\n\n"
                f"🟢 ۳ ماهه → {format_price(PREMIUM_3M)}\n"
                f"🟡 ۶ ماهه → {format_price(PREMIUM_6M)}\n"
                f"🟠 ۱۲ ماهه → {format_price(PREMIUM_12M)}"
            )
            send_inline(update.effective_chat.id, text2, buttons=[
                [{"text": f"🟢 ۳ ماهه | {format_price(PREMIUM_3M)}", "callback_data": "buy_premium_3", "style": "success"}],
                [{"text": f"🟡 ۶ ماهه | {format_price(PREMIUM_6M)}", "callback_data": "buy_premium_6", "style": "success"}],
                [{"text": f"🟠 ۱۲ ماهه | {format_price(PREMIUM_12M)}", "callback_data": "buy_premium_12", "style": "success"}],
            ])

        elif action == "stars":
            text2 = "⭐ **استارز تلگرام**\n\n" + f"💵 هر استارز: {format_price(STAR_PRICE_TOMAN)}\n\n📦 **بسته‌ها:**\n"
            buttons = []
            for pkg in STAR_PACKAGES:
                total = pkg["count"] * STAR_PRICE_TOMAN
                text2 += f"{pkg['emoji']} {pkg['label']} → {format_price(total)}\n"
                buttons.append([{
                    "text": f"{pkg['emoji']}  {pkg['label']}  |  {format_price(total)}",
                    "callback_data": f"buy_stars_{pkg['count']}",
                    "style": "success"
                }])
            send_inline(update.effective_chat.id, text2, buttons=buttons)

        elif action == "ticket":
            send_msg(update.effective_chat.id, "🎫 **تیکت پشتیبانی**\n\nپیامت رو بفرست، به ادمین میره.\n\n/cancel برای لغو")
            context.user_data["awaiting_ticket"] = True

        elif action == "balance":
            send_msg(update.effective_chat.id,
                f"💰 **موجودی حساب شما**\n\n"
                f"⭐ **استارز:** `{user.get('stars', 0)}`\n"
                f"💎 **پرمیوم:** {'✅ فعال' if user.get('premium') else '❌ غیرفعال'}")

        elif action == "sites":
            send_inline(update.effective_chat.id, "🌐 **سایت‌های ما**", buttons=sites_buttons())

        return  # ← مهم!

    # ==========================================
    # چک حالات خاص
    # ==========================================
    if context.user_data.get("changing_name"):
        context.user_data.pop("changing_name", None)
        return await change_name_new(update, context)

    if context.user_data.get("changing_pass"):
        context.user_data.pop("changing_pass", None)
        return await change_pass_old(update, context)

    if context.user_data.get("pending_approval") and update.effective_user.id == ADMIN_ID:
        pending = context.user_data.pop("pending_approval")
        oid = pending["order_id"]
        bid = pending["buyer_id"]
        u = users_db.get(bid, {})
        for o in u.get("orders", []):
            if o.get("order_id") == oid:
                o["status"] = "تایید شده"
                o["config"] = text
                break
        save_db(users_db)
        send_inline(int(bid), f"🎉 **تایید شد!**\n\n🔖 `{oid}`\n\n📦 اطلاعات تحویل:\n`{text}`")
        return

    if context.user_data.get("awaiting_ticket"):
        context.user_data.pop("awaiting_ticket", None)
        user = users_db.get(user_id, {})
        send_inline(
            ADMIN_ID,
            f"🎫 **تیکت جدید**\n\n👤 {update.effective_user.first_name}\n🆔 `{user_id}`\n🔗 @{update.effective_user.username or 'ندارد'}\n\n💬 {text}\n\n↩️ ریپلای کن."
        )
        send_reply_keyboard(update.effective_chat.id, "✅ تیکتت ارسال شد.")
        return

# ================== پاسخ ادمین به تیکت ==================
async def admin_reply_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not update.message.reply_to_message:
        return
    replied = update.message.reply_to_message
    if not replied.text or "🎫" not in replied.text:
        return
    try:
        uid = None
        for line in replied.text.split("\n"):
            if "🆔 `" in line:
                uid = line.split("`")[1]
                break
        if not uid:
            return
        send_msg(int(uid), f"📩 **پاسخ پشتیبانی:**\n\n{update.message.text}")
        await update.message.reply_text("✅ ارسال شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

# ================== کامندهای ادمین ==================
async def whoami(update, context):
    await update.message.reply_text(
        f"🆔 `{update.effective_user.id}`\n🔧 `{ADMIN_ID}`\n✅ {'بله' if update.effective_user.id == ADMIN_ID else 'نه'}",
        parse_mode="Markdown")

async def admin_test_panel(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text("⏳ تست پنل...")
    result = panel_create_user(f"test_{int(time.time())}", 1, 1)
    if result["ok"]:
        await update.message.reply_text(f"✅ پنل وصله!\n🆔 `{result['uuid']}`", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ `{result['error']}`", parse_mode="Markdown")

# ================== error handler ==================
async def error_handler(update, context):
    logger.error(f"Exception: {context.error}")

# ================== اجرا ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_username)],
            ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_password)],
            ASK_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_confirm)],
        },
        fallbacks=[CommandHandler("start", start), CommandHandler("cancel", cancel)],
    )
    pass_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^change_pass$")],
        states={
            CHANGE_PASS_OLD: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_pass_old)],
            CHANGE_PASS_NEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_pass_new)],
            CHANGE_PASS_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_pass_confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    name_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^change_name$")],
        states={CHANGE_NAME_NEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_name_new)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(pass_conv)
    app.add_handler(name_conv)
    app.add_handler(CommandHandler("testpanel", admin_test_panel))
    app.add_handler(CommandHandler("whoami", whoami))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(check_membership, pattern="^check_membership$"))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_handler(MessageHandler(filters.REPLY & filters.TEXT & filters.User(ADMIN_ID), admin_reply_ticket))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.add_error_handler(error_handler)

    print("VEXO Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main
