import os
import logging
from threading import Thread
from flask import Flask
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ==========================================
# 1. إعداد سيرفر Flask لإبقاء الخدمة نشطة 24/7
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Server is online and monitoring."

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# تشغيل السيرفر المباشر
keep_alive()

# ==========================================
# 2. إعداد السجلات (Logging) وقاعدة البيانات المقتطعة
# ==========================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ذاكرة حفظ بيانات المستخدمين لمنع الاحتيال
user_history = {}

# استدعاء التوكين بآمان من متغيرات البيئة
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ==========================================
# 3. نظام كشف تغيير الاسم واليوزر (منع الاحتيال)
# ==========================================
async def track_user_changes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    if not user or user.is_bot:
        return

    user_id = user.id
    current_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    current_username = user.username or "بدون يوزر"

    # فحص السجل المسبق للمستخدم
    if user_id in user_history:
        old_data = user_history[user_id]
        old_name = old_data.get("name")
        old_username = old_data.get("username")

        changes = []
        if old_name != current_name:
            changes.append(f"📝 **الاسم السابق:** {old_name}\n📝 **الاسم الجديد:** {current_name}")
        if old_username != current_username:
            changes.append(f"🔗 **اليوزر السابق:** @{old_username}\n🔗 **اليوزر الجديد:** @{current_username}")

        # إذا تم كشف أي تغيير وكان التفاعل داخل مجموعة
        if changes and chat and chat.type in ['group', 'supergroup']:
            alert_msg = (
                "🚨 **تنبيه أمني: كشف تغيير بيانات حساب**\n"
                "----------------------------------\n"
                f"👤 **المستخدم:** [{current_name}](tg://user?id={user_id})\n"
                f"🆔 **المعرف الرقمي:** `{user_id}`\n\n"
                "⚠️ **التغييرات التي تمت مؤخراً:**\n" +
                "\n\n".join(changes) +
                "\n\n🛑 *ملاحظة: هذا التنبيه آلي لمنع محاولات انتحال الشخصيات أو الاحتيال.*"
            )
            await context.bot.send_message(
                chat_id=chat.id,
                text=alert_msg,
                parse_mode="Markdown"
            )

    # تحديث بيانات المستخدم في السجل
    user_history[user_id] = {
        "name": current_name,
        "username": current_username
    }

# ==========================================
# 4. أمر البداية والقائمة الرئيسية (/start)
# ==========================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_info = await context.bot.get_me()
    bot_username = bot_info.username

    keyboard = [
        [InlineKeyboardButton("أضفني إلى مجموعة ➕", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("إعدادات المجموعة ✍️", callback_data="settings_page_1")],
        [
            InlineKeyboardButton("المجموعة 👥", url="https://t.me/telegram"),
            InlineKeyboardButton("القناة 📢", url="https://t.me/telegram")
        ],
        [
            InlineKeyboardButton("الدعم ⛑️", url="https://t.me/telegram"),
            InlineKeyboardButton("معلومات 💬", callback_data="info_btn")
        ],
        [InlineKeyboardButton("Languages 🇸🇦", callback_data="lang_btn")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "السلام عليكم ورحمة الله وبركاته؛\n\n"
        "مرحباً بك. نظام الإدارة والتأمين الرقمي في خدمتك.\n\n"
        "أنشئ هذا البوت بهدف فرض النظام الإداري، حماية المجموعات، والحد من محاولات التسلل والاحتيال بدقة وحزم.\n\n"
        "⚙️ **البوت تم صناعته من الصفر وتم تطويره من قبل @jkrvagner**\n\n"
        "📌 **أوامر التشغيل والإدارة:**\n"
        "اضغط على /help للوصول إلى كافة الأوامر الإدارية والتعليمات التنفيذية."
    )

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# ==========================================
# 5. صفحات الإعدادات
# ==========================================

# الصفحة الأولى للإعدادات (الصورة الثانية)
async def show_settings_page_1(query):
    keyboard = [
        [InlineKeyboardButton("القوانين 📜", callback_data="set_rules"), InlineKeyboardButton("مانع الرسائل المزعجة ✉️", callback_data="set_antispam")],
        [InlineKeyboardButton("الترحيب 💬", callback_data="set_welcome"), InlineKeyboardButton("مانع الرسائل المكررة 🗣️", callback_data="set_antiflood")],
        [InlineKeyboardButton("وداعاً 🖐️", callback_data="set_goodbye"), InlineKeyboardButton("الحروف الهجائية 🕉️", callback_data="set_charfilter")],
        [InlineKeyboardButton("التحقق Captcha 🧠", callback_data="set_captcha"), InlineKeyboardButton("القيود 🔦", callback_data="set_restrictions")],
        [InlineKeyboardButton("تقرير admin@ 🆘", callback_data="set_reports"), InlineKeyboardButton("حظر 🔐", callback_data="set_ban")],
        [InlineKeyboardButton("الوسائط 📸", callback_data="set_media"), InlineKeyboardButton("إباحية 🔞", callback_data="set_nsfw")],
        [InlineKeyboardButton("الإنذارات ❗️", callback_data="set_warns"), InlineKeyboardButton("الوضع ليلي 🌙", callback_data="set_nightmode")],
        [InlineKeyboardButton("تنبيه Tag 🔔", callback_data="set_tag"), InlineKeyboardButton("رابط المجموعة 🔗", callback_data="set_link")],
        [InlineKeyboardButton("البوت الحارس 🕵️‍♂️ NEW", callback_data="set_guardian")],
        [InlineKeyboardButton("وضع الموافقة 🎟️", callback_data="set_approval")],
        [InlineKeyboardButton("حذف الرسائل 🗑️", callback_data="set_delmsg")],
        [
            InlineKeyboardButton("Lang 🇸🇦", callback_data="lang_btn"),
            InlineKeyboardButton("إغلاق ✅", callback_data="close_menu"),
            InlineKeyboardButton("أخرى ▶️", callback_data="settings_page_2")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "⚙️ **لوحة التحكم وإعدادات المجموعة (الصفحة 1):**\n\nحدد البند الذي ترغب في ضبطه وتعديل ضوابطه الإدارية:"
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# الصفحة الثانية للإعدادات - أخرى (الصورة الثالثة)
async def show_settings_page_2(query):
    keyboard = [
        [InlineKeyboardButton("الموضوع 📦", callback_data="set_topic")],
        [InlineKeyboardButton("الكلمات المحظورة abc", callback_data="set_badwords")],
        [InlineKeyboardButton("تكرار الرسائل 🗣️", callback_data="set_repeat")],
        [InlineKeyboardButton("إدارة الأعضاء 👥", callback_data="set_members")],
        [InlineKeyboardButton("المستخدمون المتخفون 🪞", callback_data="set_ghosts")],
        [InlineKeyboardButton("مجموعة المناقشة 📣 NEW", callback_data="set_discussion")],
        [InlineKeyboardButton("الأوامر الشخصية 🧮", callback_data="set_customcmds")],
        [InlineKeyboardButton("ملصقات سحرية وصور متحركة 🎭", callback_data="set_stickers")],
        [InlineKeyboardButton("الرسائل الطويلة ✏️", callback_data="set_longmsg")],
        [InlineKeyboardButton("إدارة القنوات 📣 NEW", callback_data="set_channels")],
        [InlineKeyboardButton("أدونات 📝", callback_data="set_notes"), InlineKeyboardButton("قناة سجل المجموعة 🔍", callback_data="set_logchannel")],
        [
            InlineKeyboardButton("العودة ◀️", callback_data="settings_page_1"),
            InlineKeyboardButton("إغلاق ✅", callback_data="close_menu"),
            InlineKeyboardButton("Lang 🇸🇦", callback_data="lang_btn")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "⚙️ **لوحة التحكم وإعدادات المجموعة (الصفحة 2 - خيارات إضافية):**\n\nاختر الإعداد المتقدم المراد تعيينه:"
    await query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# ==========================================
# 6. معالج الضغط على الأزرار (Callbacks)
# ==========================================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "settings_page_1":
        await show_settings_page_1(query)
    elif data == "settings_page_2":
        await show_settings_page_2(query)
    elif data == "close_menu":
        await query.message.delete()
    elif data == "info_btn":
        await query.answer("نظام أمني رسمي مخصص لحماية وتأمين المجموعات وضبط صلاحيات الأعضاء.\nمطور البوت: @jkrvagner", show_alert=True)
    elif data == "lang_btn":
        await query.answer("اللغة المعتمدة حالياً: اللغة العربية 🇸🇦", show_alert=True)
    elif data.startswith("set_"):
        setting_key = data.replace("set_", "").upper()
        await query.answer(f"تم فتح إعدادات: {setting_key}", show_alert=True)

# ==========================================
# 7. تشغيل البوت وإدارة المعالجات
# ==========================================
def main():
    if not BOT_TOKEN:
        print("خطأ أمني: BOT_TOKEN غير موجود في متغيرات البيئة!")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # معالجة الأوامر والقوائم
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(callback_handler))

    # معالج كشف تغيير الأسماء على كافة الرسائل
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, track_user_changes))

    # بدء الاستماع للرسائل
    print("جاري تشغيل خادم البوت بنجاح...")
    application.run_polling()

if __name__ == "__main__":
    main()
    
