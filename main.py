import logging
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    filters, ContextTypes
)


TOKEN = "8953411555:AAHU1pPIZtU_qIjOPipuPV6bxr74lphNHmY"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 1. أمر الترحيب (/start)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! البوت يعمل بنجاح ومستعد لإدارة المجموعة 🚀")

# 2. الترحيب بالإعضاء الجدد تلقائياً
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"أهلاً بك يا {member.full_name} في المجموعه! 🥳✨")

# 3. توديع الأعضاء عند المغادرة
async def goodbye_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    left_member = update.message.left_chat_member
    await update.message.reply_text(f"مع السلامة {left_member.full_name} 👋")

# 4. الردود التلقائية على الكلمات
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if text == "السلام عليكم":
        await update.message.reply_text("وعليكم السلام ورحمة الله وبركاته! 🌹")
    elif text in ["هلا", "مرحبا"]:
        await update.message.reply_text("أهلاً وسهلاً بك! ✨")

# 5. كشف معلومات الحساب والرتبة (/id)
async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat = update.effective_chat
    
    # معرفة رتبة المستخدم في المجموعة
    member_status = await chat.get_member(user.id)
    role = "عضو"
    if member_status.status in ['administrator', 'creator']:
        role = "مشرف 👑"
        
    info_text = (
        f"📊 **معلومات حسابك:**\n\n"
        f"👤 الاسم: {user.full_name}\n"
        f"🆔 الآيدي (ID): `{user.id}`\n"
        f"🏷️ اليوزر: @{user.username if user.username else 'لا يوجد'}\n"
        f"🏅 الرتبة: {role}"
    )
    await update.message.reply_text(info_text, parse_mode="Markdown")

# 6. أمر الحظر (بالرد على رسالة الشخص: /ban)
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("يرجى الرد على رسالة العضو المراد حظره واستخدام /ban")
        return
    
    target_user = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.effective_chat.id, target_user.id)
    await update.message.reply_text(f"تم حظر العضو {target_user.full_name} بنجاح 🚫")

# 7. أمر الكتم (بالرد على رسالة الشخص: /mute)
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("يرجى الرد على رسالة العضو المراد كتمه واستخدام /mute")
        return
    
    target_user = update.message.reply_to_message.from_user
    permissions = ChatPermissions(can_send_messages=False)
    await context.bot.restrict_chat_member(update.effective_chat.id, target_user.id, permissions=permissions)
    await update.message.reply_text(f"تم كتم العضو {target_user.full_name} بنجاح 🔇")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    # تسجيل الأوامر والخدمات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", user_info))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    
    # الترحيب والتوديع والرد التلقائي
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    print("البوت الشامل يعمل الآن...")
    app.run_polling()
  
