import json
from api.handlers.document_handler import handle_document
from api.handlers.merge_handler import handle_merge
from api.handlers.split_handler import handle_split
from api.handlers.encrypt_handler import handle_encrypt
from api.handlers.decrypt_handler import handle_decrypt
from api.handlers.image_to_pdf_handler import handle_image_to_pdf

# قاموس يربط الأوامر بمعالجاتها
COMMAND_HANDLERS = {
    'merge': handle_merge,
    'split': handle_split,
    'encrypt': handle_encrypt,
    'decrypt': handle_decrypt,
    'img2pdf': handle_image_to_pdf,
    # أضف المزيد من الأوامر هنا
}

def handle_callback(update):
    """
    معالج الاستدعاء الرئيسي للبوت
    """
    try:
        print(f"Processing update: {json.dumps(update, indent=2)}")
        
        # تحقق من وجود الرسالة في التحديث
        if 'message' not in update:
            print("No message in update")
            return None
        
        message = update['message']
        
        # تحقق من وجود النص في الرسالة
        if 'text' in message:
            text = message['text']
            print(f"Received text: {text}")
            
            # تحقق من أن النص يبدأ بـ '/'
            if text.startswith('/'):
                # استخراج الأمر
                command = text.split(' ')[0][1:]
                print(f"Extracted command: {command}")
                
                # التحقق من وجود معالج للأمر
                if command in COMMAND_HANDLERS:
                    print(f"Calling handler for command: {command}")
                    return COMMAND_HANDLERS[command](update)
                else:
                    print(f"No handler for command: {command}")
                    print(f"Available commands: {list(COMMAND_HANDLERS.keys())}")
                    # إرسال رسالة بالأوامر المتاحة
                    return {
                        'method': 'sendMessage',
                        'chat_id': message['chat']['id'],
                        'text': f"الأمر غير معروف. الأوامر المتاحة هي: {', '.join(['/' + cmd for cmd in COMMAND_HANDLERS.keys()])}"
                    }
        
        # تحقق من وجود مستند في الرسالة
        if 'document' in message:
            print("Document received, handling document")
            return handle_document(update)
            
        # إذا لم يتم التعرف على نوع الرسالة
        print("Message type not recognized")
        return {
            'method': 'sendMessage',
            'chat_id': message['chat']['id'],
            'text': "أرسل أمرًا (مثل /merge أو /split) أو قم بإرسال ملف PDF."
        }
            
    except Exception as e:
        print(f"Error in handle_callback: {str(e)}")
        # في حالة حدوث خطأ، أرسل رسالة خطأ
        if 'message' in update and 'chat' in update['message']:
            return {
                'method': 'sendMessage',
                'chat_id': update['message']['chat']['id'],
                'text': f"حدث خطأ أثناء معالجة طلبك: {str(e)}"
            }
        return None
