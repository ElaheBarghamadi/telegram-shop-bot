from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

import db
import config
from utils import log, is_admin

user_state = {}

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 خوش آمدی", reply_markup=menu())


def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 محصولات", callback_data="products")],
        [InlineKeyboardButton("🛒 سبد", callback_data="cart")],
        [InlineKeyboardButton("🔐 ورود ادمین", callback_data="admin_login")]
    ])


# ---------- PRODUCTS ----------
async def show_products(update, context):
    for p in db.get_products():
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ افزودن", callback_data=f"add_{p[0]}")]
        ])

        if p[3]:
            await update.effective_message.reply_photo(p[3], caption=f"{p[1]} - {p[2]}", reply_markup=kb)
        else:
            await update.effective_message.reply_text(f"{p[1]} - {p[2]}", reply_markup=kb)


# ---------- CALLBACK ----------
async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    data = q.data

    if data == "products":
        await show_products(update, context)

    elif data == "cart":
        cart = db.get_cart(uid)

        text = "🛒 سبد:\n"
        total = 0

        for pid, qty in cart:
            p = db.get_product(pid)
            total += p[2] * qty
            text += f"{p[1]} x{qty}\n"

        await q.message.reply_text(text + f"\n💰 {total}")

    elif data.startswith("add_"):
        db.add_to_cart(uid, int(data.split("_")[1]))
        await q.message.reply_text("✔ اضافه شد")

    elif data == "admin_login":
        user_state[uid] = {"step": "password"}
        await q.message.reply_text("🔐 رمز ادمین؟")


# ---------- MESSAGE ----------
async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    state = user_state.get(uid)

    # login admin
    if state and state["step"] == "password":
        if text == config.ADMIN_PASSWORD:
            config.ADMINS.add(uid)
            await update.message.reply_text("✔ ادمین شدی")
        else:
            await update.message.reply_text("❌ اشتباه")
        user_state.pop(uid)
        return

    # admin panel
    if is_admin(uid):
        if text == "/add":
            user_state[uid] = {"step": "photo"}
            await update.message.reply_text("📸 عکس محصول")
            return

        if uid in user_state:
            s = user_state[uid]

            if s["step"] == "photo":
                if update.message.photo:
                    s["photo"] = update.message.photo[-1].file_id
                    s["step"] = "name"
                    await update.message.reply_text("نام؟")

            elif s["step"] == "name":
                s["name"] = text
                s["step"] = "price"
                await update.message.reply_text("قیمت؟")

            elif s["step"] == "price":
                db.add_product(s["name"], int(text), s["photo"])
                await update.message.reply_text("✔ اضافه شد")
                user_state.pop(uid)
        return


# ---------- APP ----------
app = Application.builder().token(config.BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(cb))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, msg))

db.init_db()

log("Bot started")

app.run_polling()