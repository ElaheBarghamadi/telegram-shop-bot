from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

import db
from config import BOT_TOKEN, ADMIN_ID

# ===================== STATE =====================
user_state = {}


# ===================== UI HELPERS =====================
def product_caption(p):
    return f"""
🛒 {p[1]}
💰 قیمت: {p[2]} تومان
🆔 کد: {p[0]}
"""


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 محصولات", callback_data="products")],
        [InlineKeyboardButton("🛒 سبد خرید", callback_data="cart")]
    ])


# ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 به فروشگاه ما خوش اومدی!",
        reply_markup=main_menu()
    )


# ===================== SHOW PRODUCTS =====================
async def show_products(update, context):
    products = db.get_products()

    if not products:
        await update.effective_message.reply_text("❌ محصولی وجود ندارد")
        return

    for p in products:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ افزودن به سبد", callback_data=f"add_{p[0]}")]
        ])

        if p[3]:
            await update.effective_message.reply_photo(
                photo=p[3],
                caption=product_caption(p),
                reply_markup=keyboard
            )
        else:
            await update.effective_message.reply_text(
                product_caption(p),
                reply_markup=keyboard
            )


# ===================== CALLBACK HANDLER =====================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    # 🛍 محصولات
    if data == "products":
        await query.message.reply_text("🛍 لیست محصولات:")
        await show_products(update, context)

    # 🛒 سبد خرید
    elif data == "cart":
        cart = db.get_cart(user_id)

        if not cart:
            await query.message.reply_text("🛒 سبد خرید خالیه")
            return

        text = "🛒 سبد خرید شما:\n\n"
        total = 0

        for item in cart:
            p = db.get_product(item[0])
            text += f"• {p[1]} - {p[2]} تومان\n"
            total += p[2]

        text += f"\n💰 مجموع: {total} تومان"

        await query.message.reply_text(text)

    # ➕ افزودن به سبد
    elif data.startswith("add_"):
        pid = int(data.split("_")[1])
        db.add_to_cart(user_id, pid)
        await query.message.reply_text("✅ اضافه شد به سبد خرید!")


# ===================== ADMIN FLOW =====================
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # 👨‍💼 فقط ادمین
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ دسترسی نداری")
        return

    # شروع افزودن محصول
    if text == "/add":
        user_state[user_id] = {"step": "photo"}
        await update.message.reply_text("📸 عکس محصول رو بفرست")
        return

    state = user_state.get(user_id)

    if not state:
        return

    # 📸 عکس
    if state["step"] == "photo":
        if update.message.photo:
            state["photo"] = update.message.photo[-1].file_id
            state["step"] = "name"
            await update.message.reply_text("✏️ اسم محصول")
        else:
            await update.message.reply_text("❌ فقط عکس بفرست")
        return

    # 📝 اسم
    if state["step"] == "name":
        state["name"] = text
        state["step"] = "price"
        await update.message.reply_text("💰 قیمت")
        return

    # 💰 قیمت
    if state["step"] == "price":
        state["price"] = int(text)

        db.add_product(
            state["name"],
            state["price"],
            state["photo"]
        )

        await update.message.reply_text("✅ محصول اضافه شد!")

        user_state.pop(user_id)
        return


# ===================== APP =====================
app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, message_handler))

app.run_polling()
