import telegram
import json

async def handle_callback_query(bot: telegram.Bot, update: telegram.Update, db=None):
    """معالج استجابات الأزرار (Callback Queries)"""
    callback_query = update.callback_query
    user = callback_query.from_user
    chat_id = callback_query.message.chat_id
    callback_data = callback_query.data
    
    print(f"معالجة استجابة زر من المستخدم {user.id}. البيانات: {callback_data}")
    
    try:
        # تحليل نوع الاستجابة
        if callback_data.startswith("split_"):
            # استجابة لطلب تقسيم PDF
            file_id = callback_data.replace("split_", "")
            
            # إرسال خيارات التقسيم
            await bot.send_message(
                chat_id=chat_id,
                text="الرجاء اختيار طريقة تقسيم ملف PDF:",
                reply_markup=telegram.InlineKeyboardMarkup([
                    [telegram.InlineKeyboardButton("تقسيم كل صفحة في ملف منفصل", callback_data=f"split_each_{file_id}")],
                    [telegram.InlineKeyboardButton("تقسيم حسب نطاق الصفحات", callback_data=f"split_range_{file_id}")],
                    [telegram.InlineKeyboardButton("تقسيم إلى أجزاء متساوية", callback_data=f"split_equal_{file_id}")]
                ])
            )
            
            # تحديث حالة المستخدم في قاعدة البيانات
            if db:
                db.users.update_one(
                    {"user_id": user.id},
                    {"$set": {"state": "splitting_pdf", "current_file_id": file_id}}
                )
        
        elif callback_data.startswith("merge_"):
            # استجابة لطلب دمج PDF
            file_id = callback_data.replace("merge_", "")
            
            await bot.send_message(
                chat_id=chat_id,
                text="تم إضافة الملف إلى قائمة الدمج. الرجاء إرسال ملف PDF آخر للدمج معه، أو أرسل /done لإتمام عملية الدمج."
            )
            
            # تحديث حالة المستخدم في قاعدة البيانات
            if db:
                db.users.update_one(
                    {"user_id": user.id},
                    {
                        "$set": {"state": "waiting_for_pdfs_to_merge"},
                        "$push": {"merge_files": file_id}
                    }
                )
        
        elif callback_data.startswith("encrypt_"):
            # استجابة لطلب تشفير PDF
            file_id = callback_data.replace("encrypt_", "")
            
            await bot.send_message(
                chat_id=chat_id,
                text="الرجاء إدخال كلمة المرور التي تريد استخدامها لتشفير ملف PDF:"
            )
            
            # تحديث حالة المستخدم في قاعدة البيانات
            if db:
                db.users.update_one(
                    {"user_id": user.id},
                    {"$set": {"state": "waiting_for_encrypt_password", "current_file_id": file_id}}
                )
        
        elif callback_data.startswith("decrypt_"):
            # استجابة لطلب فك تشفير PDF
            file_id = callback_data.replace("decrypt_", "")
            
            await bot.send_message(
                chat_id=chat_id,
                text="الرجاء إدخال كلمة المرور لفك تشفير ملف PDF:"
            )
            
            # تحديث حالة المستخدم في قاعدة البيانات
            if db:
                db.users.update_one(
                    {"user_id": user.id},
                    {"$set": {"state": "waiting_for_decrypt_password", "current_file_id": file_id}}
                )
        
        # إضافة المزيد من معالجات الاستجابة حسب الحاجة
        
        # إنهاء الاستجابة
        await callback_query.answer()
    
    except Exception as e:
        print(f"خطأ في معالجة استجابة الزر: {e}")
        await callback_query.answer("حدث خطأ أثناء معالجة طلبك. الرجاء المحاولة مرة أخرى.")
