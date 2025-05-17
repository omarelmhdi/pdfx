import telegram
import os
import PyPDF2
from io import BytesIO

async def handle_split_command(bot: telegram.Bot, update: telegram.Update, db=None):
    """معالج أمر /split لتقسيم ملف PDF"""
    message = update.message
    chat_id = message.chat_id
    user = message.from_user
    
    # إرسال تعليمات للمستخدم
    instructions = (
        "✂️ <b>تقسيم ملف PDF</b>\n\n"
        "هذه الميزة تسمح لك بتقسيم ملف PDF إلى عدة ملفات أصغر.\n\n"
        "<b>كيفية الاستخدام:</b>\n"
        "1. أرسل لي ملف PDF الذي تريد تقسيمه\n"
        "2. بعد إرسال الملف، سأطلب منك تحديد طريقة التقسيم\n\n"
        "<b>خيارات التقسيم:</b>\n"
        "• تقسيم حسب نطاق الصفحات (مثال: 1-3, 4-6)\n"
        "• تقسيم كل صفحة في ملف منفصل\n"
        "• تقسيم إلى عدد متساوٍ من الصفحات"
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
                {"$set": {"state": "waiting_for_pdf_to_split"}}
            )
            print(f"تم تحديث حالة المستخدم {user.id} إلى 'waiting_for_pdf_to_split'")
        except Exception as e:
            print(f"خطأ في تحديث حالة المستخدم: {e}")
