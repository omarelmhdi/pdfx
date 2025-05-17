import telegram
import os
import PyPDF2
from io import BytesIO

async def handle_merge_command(bot: telegram.Bot, update: telegram.Update, db=None):
    """معالج أمر /merge لدمج ملفات PDF"""
    message = update.message
    chat_id = message.chat_id
    user = message.from_user
    
    # إرسال تعليمات للمستخدم
    instructions = (
        "🔄 <b>دمج ملفات PDF</b>\n\n"
        "هذه الميزة تسمح لك بدمج عدة ملفات PDF في ملف واحد.\n\n"
        "<b>كيفية الاستخدام:</b>\n"
        "1. أرسل لي ملفات PDF التي تريد دمجها واحداً تلو الآخر\n"
        "2. عندما تنتهي من إرسال جميع الملفات، أرسل /done لبدء عملية الدمج\n\n"
        "<b>ملاحظة:</b> سيتم دمج الملفات بالترتيب الذي أرسلتها به."
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
                {"$set": {"state": "waiting_for_pdfs_to_merge", "merge_files": []}}
            )
            print(f"تم تحديث حالة المستخدم {user.id} إلى 'waiting_for_pdfs_to_merge'")
        except Exception as e:
            print(f"خطأ في تحديث حالة المستخدم: {e}")
