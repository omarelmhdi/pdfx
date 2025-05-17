import os
import json
import telegram
from flask import Flask, request, jsonify
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from pymongo import MongoClient

# إعداد التطبيق
app = Flask(__name__)

# استيراد معالجات الأوامر والرسائل
from api.handlers.start_handler import handle_start_command
from api.handlers.document_handler import handle_document
from api.handlers.merge_handler import handle_merge_command
from api.handlers.split_handler import handle_split_command
from api.handlers.encrypt_handler import handle_encrypt_command
from api.handlers.decrypt_handler import handle_decrypt_command
from api.handlers.image_to_pdf_handler import handle_image_to_pdf
from api.handlers.callback_handler import handle_callback_query

# استيراد متغيرات البيئة
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID")
MONGODB_URI = os.environ.get("MONGODB_URI")

# التحقق من وجود المتغيرات الأساسية
if not TELEGRAM_BOT_TOKEN:
    print("خطأ: لم يتم تعيين TELEGRAM_BOT_TOKEN في متغيرات البيئة")

# إعداد اتصال MongoDB إذا كان متاحاً
db = None
if MONGODB_URI:
    try:
        client = MongoClient(MONGODB_URI)
        db = client.pdf_bot_db
        print("تم الاتصال بقاعدة البيانات MongoDB بنجاح")
    except Exception as e:
        print(f"خطأ في الاتصال بقاعدة البيانات MongoDB: {e}")

# إنشاء كائن البوت
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

# مسار الويب هوك لاستقبال تحديثات تيليجرام
@app.route(f"/webhook/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
async def webhook_handler():
    if not bot:
        return jsonify({"status": "error", "message": "لم يتم تهيئة البوت. توكن مفقود."}), 500

    if request.method == "POST":
        update_json = request.get_json(force=True)
        try:
            update = telegram.Update.de_json(update_json, bot)
            print(f"تم استلام تحديث: {update.update_id}")
            
            # معالجة الأوامر
            if update.message:
                chat_id = update.message.chat_id
                
                # التحقق من الأوامر
                if update.message.text:
                    text = update.message.text
                    print(f"رسالة من {chat_id}: {text}")
                    
                    if text.startswith("/start"):
                        await handle_start_command(bot, update, db, ADMIN_USER_ID)
                    elif text.startswith("/merge"):
                        await handle_merge_command(bot, update, db)
                    elif text.startswith("/split"):
                        await handle_split_command(bot, update, db)
                    elif text.startswith("/encrypt"):
                        await handle_encrypt_command(bot, update, db)
                    elif text.startswith("/decrypt"):
                        await handle_decrypt_command(bot, update, db)
                    elif text.startswith("/imagetopdf"):
                        await handle_image_to_pdf(bot, update, db)
                
                # معالجة المستندات (PDF)
                elif update.message.document:
                    await handle_document(bot, update, db)
                
                # معالجة الصور (للتحويل إلى PDF)
                elif update.message.photo:
                    await handle_image_to_pdf(bot, update, db)
            
            # معالجة استجابات الأزرار
            elif update.callback_query:
                await handle_callback_query(bot, update, db)
            
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            print(f"خطأ في معالجة التحديث: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"status": "error", "message": str(e)}), 500
    
    return jsonify({"status": "error", "message": "طريقة طلب غير صالحة"}), 405

# الصفحة الرئيسية للتحقق من حالة البوت
@app.route("/")
def index():
    return "مرحباً! هذا هو معالج الويب هوك لبوت PDF. البوت يعمل بشكل صحيح.", 200

# لا حاجة لـ app.run() هنا لأن Vercel ستقوم بتشغيل التطبيق
