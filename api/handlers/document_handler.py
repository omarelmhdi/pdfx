import telegram
import os
import PyPDF2
from io import BytesIO

async def handle_document(bot: telegram.Bot, update: telegram.Update, db=None):
    """معالج استقبال المستندات (PDF)"""
    message = update.message
    chat_id = message.chat_id
    user = message.from_user
    document = message.document
    
    print(f"معالجة مستند من المستخدم {user.id} في المحادثة {chat_id}. معرف الملف: {document.file_id}")
    
    try:
        file_name = document.file_name
        mime_type = document.mime_type
        
        # التحقق من نوع الملف
        if mime_type == "application/pdf":
            # إرسال رسالة تأكيد استلام الملف
            await bot.send_message(
                chat_id=chat_id,
                text=f"تم استلام ملف PDF: {file_name}\n\nالرجاء اختيار العملية التي تريد تنفيذها على هذا الملف:",
                reply_markup=telegram.InlineKeyboardMarkup([
                    [
                        telegram.InlineKeyboardButton("تقسيم PDF", callback_data=f"split_{document.file_id}"),
                        telegram.InlineKeyboardButton("تشفير PDF", callback_data=f"encrypt_{document.file_id}")
                    ],
                    [
                        telegram.InlineKeyboardButton("دمج مع PDF آخر", callback_data=f"merge_{document.file_id}"),
                        telegram.InlineKeyboardButton("فك تشفير PDF", callback_data=f"decrypt_{document.file_id}")
                    ]
                ])
            )
            
            # حفظ معلومات الملف في قاعدة البيانات إذا كانت متاحة
            if db:
                try:
                    file_data = {
                        "user_id": user.id,
                        "file_id": document.file_id,
                        "file_name": file_name,
                        "mime_type": mime_type,
                        "timestamp": telegram.utils.helpers.to_timestamp(message.date)
                    }
                    
                    db.files.insert_one(file_data)
                    print(f"تم حفظ معلومات الملف {document.file_id} في قاعدة البيانات")
                except Exception as e:
                    print(f"خطأ في حفظ معلومات الملف: {e}")
        else:
            # إذا لم يكن الملف PDF
            await bot.send_message(
                chat_id=chat_id,
                text=f"عذراً، هذا البوت يعمل فقط مع ملفات PDF. الملف المرسل هو من نوع {mime_type}."
            )
    
    except Exception as e:
        print(f"خطأ في معالجة المستند: {e}")
        await bot.send_message(
            chat_id=chat_id,
            text=f"حدث خطأ أثناء معالجة المستند: {e}"
        )
