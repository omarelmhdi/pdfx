import telegram

async def handle_start_command(bot: telegram.Bot, update: telegram.Update, db=None, admin_id=None):
    """معالج أمر /start"""
    message = update.message
    chat_id = message.chat_id
    user = message.from_user
    
    # تحية المستخدم
    welcome_text = f"مرحباً {user.first_name}! 👋\n\n"
    welcome_text += "أنا بوت معالجة ملفات PDF. يمكنني مساعدتك في العديد من المهام مثل:\n\n"
    welcome_text += "• دمج عدة ملفات PDF معاً 📄\n"
    welcome_text += "• تقسيم ملف PDF إلى عدة ملفات 📂\n"
    welcome_text += "• تشفير ملفات PDF 🔐\n"
    welcome_text += "• فك تشفير ملفات PDF 🔓\n"
    welcome_text += "• تحويل الصور إلى PDF 🖼️\n\n"
    welcome_text += "أرسل لي أمر من الأوامر التالية للبدء:\n"
    welcome_text += "/merge - لدمج ملفات PDF\n"
    welcome_text += "/split - لتقسيم ملف PDF\n"
    welcome_text += "/encrypt - لتشفير ملف PDF\n"
    welcome_text += "/decrypt - لفك تشفير ملف PDF\n"
    welcome_text += "/imagetopdf - لتحويل صورة إلى PDF\n"
    
    # إضافة رسالة خاصة للمشرف
    if admin_id and str(chat_id) == str(admin_id):
        welcome_text += "\n🔧 أنت المشرف على هذا البوت!"
    
    # حفظ بيانات المستخدم في قاعدة البيانات إذا كانت متاحة
    if db:
        try:
            user_data = {
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language_code": user.language_code,
                "last_interaction": telegram.utils.helpers.to_timestamp(message.date),
                "is_admin": str(chat_id) == str(admin_id)
            }
            
            # إدراج أو تحديث بيانات المستخدم
            db.users.update_one(
                {"user_id": user.id},
                {"$set": user_data},
                upsert=True
            )
            print(f"تم تحديث بيانات المستخدم {user.id} في قاعدة البيانات")
        except Exception as e:
            print(f"خطأ في تحديث بيانات المستخدم: {e}")
    
    # إرسال رسالة الترحيب
    await bot.send_message(
        chat_id=chat_id,
        text=welcome_text,
        parse_mode=telegram.constants.ParseMode.HTML
    )
    
    print(f"تم إرسال رسالة الترحيب إلى المستخدم {chat_id}")
