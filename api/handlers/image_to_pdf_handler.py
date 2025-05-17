import telegram
import os
from PIL import Image
from io import BytesIO
import tempfile

async def handle_image_to_pdf(bot: telegram.Bot, update: telegram.Update, db=None):
    """معالج أمر /imagetopdf لتحويل الصور إلى PDF"""
    message = update.message
    chat_id = message.chat_id
    user = message.from_user
    
    # إرسال تعليمات للمستخدم
    instructions = (
        "🖼️ <b>تحويل الصور إلى PDF</b>\n\n"
        "هذه الميزة تسمح لك بتحويل صورة أو مجموعة من الصور إلى ملف PDF.\n\n"
        "<b>كيفية الاستخدام:</b>\n"
        "1. أرسل لي الصور التي تريد تحويلها إلى PDF واحداً تلو الآخر\n"
        "2. عندما تنتهي من إرسال جميع الصور، أرسل /done لبدء عملية التحويل\n\n"
        "<b>ملاحظة:</b> سيتم ترتيب الصور في ملف PDF حسب ترتيب إرسالها."
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
                {"$set": {"state": "waiting_for_images", "images": []}}
            )
            print(f"تم تحديث حالة المستخدم {user.id} إلى 'waiting_for_images'")
        except Exception as e:
            print(f"خطأ في تحديث حالة المستخدم: {e}")
