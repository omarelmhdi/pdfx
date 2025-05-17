import os
import tempfile
from io import BytesIO
import PyPDF2

async def merge_pdfs(bot, chat_id, file_ids):
    """
    دمج ملفات PDF متعددة في ملف واحد
    
    Args:
        bot: كائن البوت
        chat_id: معرف المحادثة
        file_ids: قائمة بمعرفات ملفات PDF
        
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF المدمج
    """
    merger = PyPDF2.PdfMerger()
    
    # إرسال رسالة للمستخدم
    status_message = await bot.send_message(
        chat_id=chat_id,
        text="جاري دمج الملفات... ⏳"
    )
    
    try:
        # تنزيل وإضافة كل ملف PDF
        for i, file_id in enumerate(file_ids):
            # تحديث حالة التقدم
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_message.message_id,
                text=f"جاري معالجة الملف {i+1} من {len(file_ids)}... ⏳"
            )
            
            # تنزيل الملف
            file = await bot.get_file(file_id)
            file_content = await file.download_as_bytearray()
            
            # إضافة الملف إلى الدمج
            pdf_bytes = BytesIO(file_content)
            merger.append(pdf_bytes)
    
        # إنشاء ملف PDF المدمج
        merged_pdf = BytesIO()
        merger.write(merged_pdf)
        merged_pdf.seek(0)
        
        return merged_pdf
    
    except Exception as e:
        print(f"خطأ في دمج ملفات PDF: {e}")
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"حدث خطأ أثناء دمج الملفات: {e}"
        )
        return None
    finally:
        merger.close()

async def split_pdf(bot, chat_id, file_id, split_method, split_params=None):
    """
    تقسيم ملف PDF حسب الطريقة المحددة
    
    Args:
        bot: كائن البوت
        chat_id: معرف المحادثة
        file_id: معرف ملف PDF
        split_method: طريقة التقسيم ('each', 'range', 'equal')
        split_params: معلمات إضافية للتقسيم (مثل النطاقات أو عدد الأجزاء)
        
    Returns:
        list: قائمة بكائنات BytesIO تحتوي على ملفات PDF المقسمة
    """
    # إرسال رسالة للمستخدم
    status_message = await bot.send_message(
        chat_id=chat_id,
        text="جاري تقسيم الملف... ⏳"
    )
    
    try:
        # تنزيل الملف
        file = await bot.get_file(file_id)
        file_content = await file.download_as_bytearray()
        
        # فتح ملف PDF
        pdf_bytes = BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        total_pages = len(pdf_reader.pages)
        
        split_pdfs = []
        
        # تقسيم حسب الطريقة المحددة
        if split_method == 'each':
            # تقسيم كل صفحة في ملف منفصل
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_message.message_id,
                text=f"جاري تقسيم الملف إلى {total_pages} ملف... ⏳"
            )
            
            for page_num in range(total_pages):
                pdf_writer = PyPDF2.PdfWriter()
                pdf_writer.add_page(pdf_reader.pages[page_num])
                
                output = BytesIO()
                pdf_writer.write(output)
                output.seek(0)
                split_pdfs.append(output)
        
        elif split_method == 'range':
            # تقسيم حسب نطاقات الصفحات
            ranges = split_params.split(',')
            
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_message.message_id,
                text=f"جاري تقسيم الملف حسب النطاقات المحددة... ⏳"
            )
            
            for i, page_range in enumerate(ranges):
                pdf_writer = PyPDF2.PdfWriter()
                
                # تحليل النطاق (مثال: "1-3")
                start, end = map(int, page_range.strip().split('-'))
                # تعديل الفهرس ليبدأ من 0
                start -= 1
                
                # التحقق من صحة النطاق
                if start < 0 or end > total_pages:
                    continue
                
                # إضافة الصفحات في النطاق
                for page_num in range(start, end):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                
                output = BytesIO()
                pdf_writer.write(output)
                output.seek(0)
                split_pdfs.append(output)
        
        elif split_method == 'equal':
            # تقسيم إلى أجزاء متساوية
            parts = int(split_params)
            pages_per_part = total_pages // parts
            
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_message.message_id,
                text=f"جاري تقسيم الملف إلى {parts} أجزاء متساوية... ⏳"
            )
            
            for i in range(parts):
                pdf_writer = PyPDF2.PdfWriter()
                
                # تحديد نطاق الصفحات لهذا الجزء
                start = i * pages_per_part
                end = (i + 1) * pages_per_part if i < parts - 1 else total_pages
                
                # إضافة الصفحات في النطاق
                for page_num in range(start, end):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                
                output = BytesIO()
                pdf_writer.write(output)
                output.seek(0)
                split_pdfs.append(output)
        
        return split_pdfs
    
    except Exception as e:
        print(f"خطأ في تقسيم ملف PDF: {e}")
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"حدث خطأ أثناء تقسيم الملف: {e}"
        )
        return None

async def encrypt_pdf(bot, chat_id, file_id, password):
    """
    تشفير ملف PDF بكلمة مرور
    
    Args:
        bot: كائن البوت
        chat_id: معرف المحادثة
        file_id: معرف ملف PDF
        password: كلمة المرور للتشفير
        
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF المشفر
    """
    # إرسال رسالة للمستخدم
    status_message = await bot.send_message(
        chat_id=chat_id,
        text="جاري تشفير الملف... ⏳"
    )
    
    try:
        # تنزيل الملف
        file = await bot.get_file(file_id)
        file_content = await file.download_as_bytearray()
        
        # فتح ملف PDF
        pdf_bytes = BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        
        # إنشاء ملف PDF جديد مع التشفير
        pdf_writer = PyPDF2.PdfWriter()
        
        # نسخ جميع الصفحات
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        
        # تطبيق التشفير
        pdf_writer.encrypt(password)
        
        # حفظ الملف المشفر
        encrypted_pdf = BytesIO()
        pdf_writer.write(encrypted_pdf)
        encrypted_pdf.seek(0)
        
        return encrypted_pdf
    
    except Exception as e:
        print(f"خطأ في تشفير ملف PDF: {e}")
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"حدث خطأ أثناء تشفير الملف: {e}"
        )
        return None

async def decrypt_pdf(bot, chat_id, file_id, password):
    """
    فك تشفير ملف PDF
    
    Args:
        bot: كائن البوت
        chat_id: معرف المحادثة
        file_id: معرف ملف PDF
        password: كلمة المرور لفك التشفير
        
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF غير المشفر
    """
    # إرسال رسالة للمستخدم
    status_message = await bot.send_message(
        chat_id=chat_id,
        text="جاري فك تشفير الملف... ⏳"
    )
    
    try:
        # تنزيل الملف
        file = await bot.get_file(file_id)
        file_content = await file.download_as_bytearray()
        
        # فتح ملف PDF
        pdf_bytes = BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_bytes)
        
        # محاولة فك التشفير
        if pdf_reader.is_encrypted:
            success = pdf_reader.decrypt(password)
            if not success:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=status_message.message_id,
                    text="كلمة المرور غير صحيحة. الرجاء المحاولة مرة أخرى."
                )
                return None
        
        # إنشاء ملف PDF جديد بدون تشفير
        pdf_writer = PyPDF2.PdfWriter()
        
        # نسخ جميع الصفحات
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        
        # حفظ الملف غير المشفر
        decrypted_pdf = BytesIO()
        pdf_writer.write(decrypted_pdf)
        decrypted_pdf.seek(0)
        
        return decrypted_pdf
    
    except Exception as e:
        print(f"خطأ في فك تشفير ملف PDF: {e}")
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"حدث خطأ أثناء فك تشفير الملف: {e}"
        )
        return None

async def images_to_pdf(bot, chat_id, image_file_ids):
    """
    تحويل مجموعة من الصور إلى ملف PDF
    
    Args:
        bot: كائن البوت
        chat_id: معرف المحادثة
        image_file_ids: قائمة بمعرفات ملفات الصور
        
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF
    """
    from PIL import Image
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    
    # إرسال رسالة للمستخدم
    status_message = await bot.send_message(
        chat_id=chat_id,
        text="جاري تحويل الصور إلى PDF... ⏳"
    )
    
    try:
        # إنشاء ملف PDF مؤقت
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
            tmp_pdf_path = tmp_pdf.name
        
        # إنشاء ملف PDF
        c = canvas.Canvas(tmp_pdf_path, pagesize=letter)
        width, height = letter
        
        # معالجة كل صورة
        for i, file_id in enumerate(image_file_ids):
            # تحديث حالة التقدم
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_message.message_id,
                text=f"جاري معالجة الصورة {i+1} من {len(image_file_ids)}... ⏳"
            )
            
            # تنزيل الصورة
            file = await bot.get_file(file_id)
            file_content = await file.download_as_bytearray()
            
            # حفظ الصورة مؤقتاً
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_img:
                tmp_img.write(file_content)
                tmp_img_path = tmp_img.name
            
            # فتح الصورة وإضافتها إلى PDF
            img = Image.open(tmp_img_path)
            
            # تغيير حجم الصورة لتناسب الصفحة مع الحفاظ على النسبة
            img_width, img_height = img.size
            aspect = img_width / float(img_height)
            
            if aspect > 1:  # صورة أفقية
                new_width = width - 50  # هامش
                new_height = new_width / aspect
            else:  # صورة عمودية
                new_height = height - 50  # هامش
                new_width = new_height * aspect
            
            # حساب موضع الصورة (توسيط)
            x = (width - new_width) / 2
            y = (height - new_height) / 2
            
            # إضافة الصورة إلى PDF
            c.drawImage(tmp_img_path, x, y, width=new_width, height=new_height)
            
            # إضافة صفحة جديدة إذا لم تكن هذه الصورة الأخيرة
            if i < len(image_file_ids) - 1:
                c.showPage()
            
            # حذف الملف المؤقت
            os.unlink(tmp_img_path)
        
        # حفظ PDF
        c.save()
        
        # قراءة الملف المحفوظ
        with open(tmp_pdf_path, 'rb') as f:
            pdf_bytes = BytesIO(f.read())
        
        # حذف الملف المؤقت
        os.unlink(tmp_pdf_path)
        
        pdf_bytes.seek(0)
        return pdf_bytes
    
    except Exception as e:
        print(f"خطأ في تحويل الصور إلى PDF: {e}")
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"حدث خطأ أثناء تحويل الصور إلى PDF: {e}"
        )
        return None
