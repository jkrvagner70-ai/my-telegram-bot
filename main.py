from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()  # تشغيل السيرفر الوهمي في الخلفية

import logging
import re
from collections import defaultdict
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# إعداد التسجيل (Logging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ==================== 🔑 ضع التوكن هنا ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ==========================================================

# ذاكرة لتخزين أسماء وأيوزرات الأعضاء لكشف التغييرات 🕵️‍♂️
user_cache = {}

# إعدادات وقواعد بيانات الجروبات المؤقتة 💾
chat_settings = defaultdict(lambda: {
    "anti_link": True,
    "rules": "مفيش قوانين محددة لسه يا غالي! 📜",
    "replies": {
        "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته يا بعد قلبي! 💖🖐️",
        "هلا": "أهلاً وسهلاً! نورت المكان يا عسل ✨🔥",
        "منور": "بنورك يا قلبي والله! 🌟❤️",
        "البوت": "عيون البوت! تؤمرني بإيه؟ 🤖⚡"
    }
})

# 1️⃣ قائمة الأوامر الرسمية في زر Menu 🎯
async def post_init(application: Application):
    commands = [
        BotCommand("start", "بداية البوت والترحيب 🚀"),
        BotCommand("rank", "معرفة رتبتك ومعلوماتك 👑"),
        BotCommand("rules", "عرض قوانين الجروب 📜"),
        BotCommand("setrules", "تعديل القوانين (للمشرفين) ✏️"),
        BotCommand("addreply", "إضافة رد تلقائي (للمشرفين) 💬"),
        BotCommand("delreply", "حذف رد تلقائي (للمشرفين) ❌"),
        BotCommand("settings", "إعدادات الحماية ⚙️"),
    ]
    await application.bot.set_my_commands(commands)

# 2️⃣ أمر /start 🥳
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "يا هلا ويا مرحبا بيك يا غالي! 🥳🔥\n\n"
        "أنا **بوت الحماية والتسلية** لجروبك! 🤖⚡\n"
        "شغلي أحمي الجروب، أرحب بالأعضاء، وأقفش أي حد يغير اسمه أو يوزره! 🕵️‍♂️💥\n\n"
        "📌 **الخصائص والوظائف اللي أقدر أعملها:**\n"
        "✨ **كشف التغيرات:** لو حد غير اسمه أو يوزره هفضحه بالجروب فوراً! 📢\n"
        "👑 **الرتب:** تقدر تعرف رتبتك بأمر `/rank`\n"
        "🛑 **الحماية:** منع الروابط والإعلانات التلقائية\n"
        "💬 **ردود ذكية:** ردود تلقائية تقدر تضيفها بنفسك\n"
        "👋 **ترحيب ووداع:** بالاسم واليوزر بشكل شيك\n\n"
        "ضيفني لجروبك وارفعني **مشرف (Admin)** عشان أشتغل معاك فل الفل! 🚀"
    )
    
    keyboard = [
        [InlineKeyboardButton("➕ ضيف البوت لجروبك من هنا", url=f"https://t.me/{context.bot.username}?startgroup=true")]
    ]
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

# 3️⃣ معرفة رتبة المستخدم 👑
async def get_user_rank(chat_id, user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status == ChatMemberStatus.OWNER:
            return "المالك الأصلي 👑🔥"
        elif member.status == ChatMemberStatus.ADMINISTRATOR:
            return "مشرف الجروب 👮‍♂️⚡"
        else:
            return "عضو منورنا 👤✨"
    except:
        return "عضو 👤"

async def rank_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    rank = await get_user_rank(chat_id, user.id, context)
    username = f"@{user.username}" if user.username else "مفيش يوزر ❌"
    
    text = (
        f"🏷️ **بطاقة معلوماتك يا بطل:**\n\n"
        f"👤 **الاسم:** {user.first_name}\n"
        f"ال **اليوزر:** {username}\n"
        f"🆔 **الأيدي (ID):** `{user.id}`\n"
        f"🎖️ **الرتبة:** {rank}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# 4️⃣ الترحيب بالأعضاء الجدد 👋
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text("أنا جيت يا شباب! 🥳🔥 ارفعوني مشرف عشان أحمي الجروب بسرعة 🚀")
            continue
            
        username = f"@{member.username}" if member.username else "من غير يوزر"
        text = (
            f"يا ألف نهار أبيض! 🎉✨\n"
            f"نورت الجروب يا غالي **{member.first_name}** ({username}) ❤️\n\n"
            f"أهلاً بيك معانا، نسينا نكتمك بالقهوة! ☕️😂\n"
            f"اطمئن على القوانين من أمر `/rules` وانسجم معانا! 🔥"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# 5️⃣ وداع الأعضاء عند المغادرة 🥹👋
async def goodbye_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.message.left_chat_member
    if member.id == context.bot.id:
        return
        
    username = f"@{member.username}" if member.username else ""
    text = f"مع السلامة يا **{member.first_name}** {username} 🥹👋\nتوصل بالسلامة يا غالي ونتمنى نشوفك تاني قريباً! 💔"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

# 6️⃣ إضافة وحذف الردود التلقائية 💬
async def add_reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    member = await context.bot.get_chat_member(chat_id, user_id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await update.message.reply_text("❌ ده أمر للمشرفين بس يا بطل!")
        return

    # صيغة الأمر: /addreply الكلمة | الرد
    text = " ".join(context.args)
    if "|" not in text:
        await update.message.reply_text("⚠️ **الطريقة الصح:**\n`/addreply الكلمة | الرد بتاعها`\n\nمثال:\n`/addreply منور | بنورك يا عسل`", parse_mode=ParseMode.MARKDOWN)
        return

    word, reply = map(str.strip, text.split("|", 1))
    chat_settings[chat_id]["replies"][word.lower()] = reply
    await update.message.reply_text(f"✅ تم إضافة الرد بنجاح!\n\n🔹 **عند كتابة:** {word}\n🔹 **البوت هيرد بـ:** {reply}")

# 7️⃣ معالجة الرسائل (كشف كسر الحماية، كشف التغييرات، والردود) 🕵️‍♂️🛑
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text
    user_id = user.id

    # --- أ: كشف تغيير الاسم أو اليوزر 🕵️‍♂️ ---
    current_name = user.first_name or ""
    current_username = f"@{user.username}" if user.username else "مفيش يوزر"

    if user_id in user_cache:
        old_data = user_cache[user_id]
        changes = []
        if old_data["name"] != current_name:
            changes.append(f"✏️ **الاسم القديم:** `{old_data['name']}`\n✏️ **الاسم الجديد:** `{current_name}`")
        if old_data["username"] != current_username:
            changes.append(f"ر **اليوزر القديم:** `{old_data['username']}`\nر **اليوزر الجديد:** `{current_username}`")

        if changes:
            alert = (
                f"🚨 **قفشة جديدة! العضو ده غير بياناته توه!** 📢\n\n"
                f"👤 **العضو:** {current_name} ({current_username})\n\n" + "\n\n".join(changes)
            )
            await update.message.reply_text(alert, parse_mode=ParseMode.MARKDOWN)

    # تحديث البيانات المخزنة
    user_cache[user_id] = {"name": current_name, "username": current_username}

    # --- ب: الحماية من الروابط (Anti-Link) 🛑 ---
    settings = chat_settings[chat_id]
    if settings["anti_link"]:
        # التحقق لو العضو مش مشرف
        member = await context.bot.get_chat_member(chat_id, user_id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            link_pattern = r"(https?://|www\.|t\.me/)"
            if re.search(link_pattern, text):
                try:
                    await update.message.delete()
                    await context.bot.send_message(
                        chat_id, 
                        f"⛔ ممنوع نشر الروابط هنا يا **{user.first_name}**! مسحت رسالتك 🚫"
                    )
                    return
                except Exception:
                    pass

    # --- ج: الردود التلقائية 💬 ---
    clean_text = text.strip().lower()
    replies = settings["replies"]
    if clean_text in replies:
        await update.message.reply_text(replies[clean_text])

# 8️⃣ أوامر القوانين والإعدادات 📜⚙️
async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    rules = chat_settings[chat_id]["rules"]
    await update.message.reply_text(f"📜 **قوانين الجروب:**\n\n{rules}", parse_mode=ParseMode.MARKDOWN)

async def setrules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    member = await context.bot.get_chat_member(chat_id, user_id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await update.message.reply_text("❌ للمشرفين بس يا بطل!")
        return

    new_rules = " ".join(context.args)
    if not new_rules:
        await update.message.reply_text("⚠️ اكتب القوانين بعد الأمر يا غالي!")
        return

    chat_settings[chat_id]["rules"] = new_rules
    await update.message.reply_text("✅ تم حفظ القوانين الجديدة بنجاح! 🎉")

# تشغيل البوت 🚀
def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # الأوامر الأساسية
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("rank", rank_command))
    app.add_handler(CommandHandler("rules", rules_command))
    app.add_handler(CommandHandler("setrules", setrules_command))
    app.add_handler(CommandHandler("addreply", add_reply_command))

    # الترحب والوداع
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye_member))

    # فحص الرسائل المباشر
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    print("🤖 البوت شغال الآن بنجاح...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
