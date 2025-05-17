import telegram
import os
from cryptography.fernet import Fernet
from io import BytesIO

async def handle_decrypt_command(bot: telegram.Bot, update: telegram.Update, db=None):
    """معالج أمر /decrypt لفك تشفير ملف PDF"""
    message = update.message
    chat_id = message.chat_id
    user = message.from_user
    
    # إرسال تعليمات للمستخدم
    instructions = (
        "🔓 <b>فك تشفير ملف PDF</b>\n\n"
        "هذه الميزة تسمح لك بفك تشفير ملف PDF محمي بكلمة مرور.\n\n"
        "<b>كيفية الاستخدام:</b>\n"
        "1. أرسل لي ملف PDF المشفر الذي تريد فك تشفيره\n"
        "2. بعد إرسال الملف، سأطلب منك إدخال كلمة المرور\n\n"
        "<b>ملاحظة:</b> يجب إدخال كلمة المرور الصحيحة التي تم استخدامها لتشفير الملف."
    )
    
    await bot.send_message(
        chat_id=chat_id,
        text=instructions,
        parse_mode=telegram.constants.ParseMode.HTML
    )
    
    # تحديث حالة المستخدم في قاعدة البيانات
    if db:
        try:
            db.users.update_one(
                {"user_id": user.id},
                {"$set": {"state": "waiting_for_pdf_to_decrypt"}}
            )
            print(f"تم تحديث حالة المستخدم {user.id} إلى 'waiting_for_pdf_to_decrypt'")
        except Exception as e:
            print(f"خطأ في تحديث حالة المستخدم: {e}")
