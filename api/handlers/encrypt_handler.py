import telegram
import os
from cryptography.fernet import Fernet
from io import BytesIO

async def handle_encrypt_command(bot: telegram.Bot, update: telegram.Update, db=None):
    """معالج أمر /encrypt لتشفير ملف PDF"""
    message = update.message
    chat_id = message.chat_id
    user = message.from_user
    
    # إرسال تعليمات للمستخدم
    instructions = (
        "🔒 <b>تشفير ملف PDF</b>\n\n"
        "هذه الميزة تسمح لك بتشفير ملف PDF بكلمة مرور لحمايته.\n\n"
        "<b>كيفية الاستخدام:</b>\n"
        "1. أرسل لي ملف PDF الذي تريد تشفيره\n"
        "2. بعد إرسال الملف، سأطلب منك إدخال كلمة المرور التي تريد استخدامها\n\n"
        "<b>ملاحظة:</b> تأكد من حفظ كلمة المرور في مكان آمن، حيث ستحتاجها لفتح الملف لاحقاً."
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
                {"$set": {"state": "waiting_for_pdf_to_encrypt"}}
            )
            print(f"تم تحديث حالة المستخدم {user.id} إلى 'waiting_for_pdf_to_encrypt'")
        except Exception as e:
            print(f"خطأ في تحديث حالة المستخدم: {e}")
