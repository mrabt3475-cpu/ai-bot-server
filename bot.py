"""
🤖 AI Bot - بوت ذكاء اصطناعي متكامل
يشبه Mira - مساعد ذكي في تليجرام
"""

import os
import json
import asyncio
import aiohttp
import requests
import base64
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, BotCommand, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ============== CONFIGURATION ==============
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

# ============== DATA STORAGE ==============
DATA_FILE = 'ai_bot_data.json'

def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'users': {}, 'conversations': {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_data(user_id):
    data = load_data()
    if str(user_id) not in data['users']:
        data['users'][str(user_id)] = {
            'name': '',
            'age': None,
            'city': '',
            'interests': [],
            'preferences': {},
            'balance': 100  # رصيد تجريبي
        }
    return data['users'][str(user_id)]

def save_user_data(user_id, user_data):
    data = load_data()
    data['users'][str(user_id)] = user_data
    save_data(data)

# ============== KEYBOARDS ==============
def get_main_menu():
    keyboard = [
        [KeyboardButton("💬 محادثة"), KeyboardButton("🎨 رسم")],
        [KeyboardButton("🎵 أغنية"), KeyboardButton("🌐 بحث")],
        [KeyboardButton("👤 ملفي"), KeyboardButton("💰 رصيدي")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_menu():
    keyboard = [[KeyboardButton("🔙 رجوع")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_image_menu():
    keyboard = [
        [InlineKeyboardButton("🎨 أنمي", callback_data="img_anime")],
        [InlineKeyboardButton("🖼️ واقعي", callback_data="img_real")],
        [InlineKeyboardButton("🏞️ منظر", callback_data="img_landscape")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ============== AI CHAT ==============
async def chat_with_ai(user_id, message):
    """محادثة مع الذكاء الاصطناعي"""
    data = load_data()
    user_data = get_user_data(user_id)
    
    # بناء سياق المحادثة
    context = f"أنت Mira - مساعد ذكي ودود. "
    if user_data.get('name'):
        context += f"اسم المستخدم {user_data['name']}. "
    if user_data.get('interests'):
        context += f"اهتماماته: {', '.join(user_data['interests'])}. "
    
    context += f"\n\nالمستخدم يقول: {message}"
    
    # إذا يوجد OpenAI API
    if OPENAI_API_KEY:
        try:
            headers = {
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            }
            payload = {
                'model': 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': context}],
                'max_tokens': 500
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
        except Exception as e:
            pass
    
    # ردود افتراضية ذكية
    responses = [
        "🤔 سؤال رائع! دعني أفكر...",
        "✨ فكرة جيدة!",
        "😅 معك حق، هذا مهم!",
        "💡 ممتاز! تريد أن أشرح أكثر؟",
        "🔥 أحب هذه الفكرة!",
        "📝 سأساعدك في هذا!",
        "👍 تمام، فهمتك!",
        "🌟 سؤال ذكي!",
    ]
    
    # ردود بسيطة
    lower_msg = message.lower()
    if any(word in lower_msg for word in ['مرحبا', 'اهلا', 'hello', 'hi', 'السلام']):
        return f"أهلاً! 👋 كيف أقدر أساعدك؟"
    elif any(word in lower_msg for word in ['شكرا', 'thanks', 'thank']):
        return "العفو! 😊 أي وقت!
    elif 'اسمك' in lower_msg or 'who are you' in lower_msg:
        return "أنا Mira - مساعدك الذكي! 🤖✨"
    elif 'كيف' in lower_msg and 'حالك' in lower_msg:
        return "الحمد لله بخير! 😊 وأنت؟"
    
    import random
    return random.choice(responses) + f"\n\n(يمكنني الإجابة بشكل أفضل مع OpenAI API)"

# ============== IMAGE GENERATION ==============
async def generate_image(prompt, style="anime"):
    """إنشاء صورة بالذكاء الاصطناعي"""
    # استخدام DALL-E API إذا توفر
    if OPENAI_API_KEY:
        try:
            headers = {
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            style_prompts = {
                'anime': f"anime style, {prompt}, colorful, detailed",
                'real': f"photorealistic, {prompt}, high quality",
                'landscape': f"beautiful landscape, {prompt}, stunning"
            }
            
            full_prompt = style_prompts.get(style, prompt)
            
            payload = {
                'prompt': full_prompt,
                'n': 1,
                'size': '1024x1024'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.openai.com/v1/images/generations',
                    headers=headers,
                    json=payload,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['data'][0]['url']
        except Exception as e:
            return f"Error: {str(e)}"
    
    return None

# ============== MUSIC GENERATION ==============
async def generate_music(prompt, duration=15):
    """إنشاء موسيقى بالذكاء الاصطناعي"""
    # Placeholder - يتطلب API خاص
    return f"🎵 يمكن إنشاء موسيقى: {prompt}\n(يتطلب API خاص)"

# ============== WEB SEARCH ==============
async def search_web(query):
    """البحث في الإنترنت"""
    url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                return data.get('AbstractText', data.get('Answer', 'لم أجد نتائج'))
    except Exception as e:
        return f"خطأ في البحث: {str(e)}"

# ============== VOICE HANDLING ==============
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل الصوتية"""
    await update.message.reply_text("🎤 استلمت صوتك! جاري المعالجة...")
    # يتطلب تحويل الصوت لنص - يمكن استخدام Google Speech API
    await update.message.reply_text(
        "🔧 تحويل الصوت لنص يتطلب إعداد Google Speech API\n\n"
        "هل تريد المتابعة محادثة نصية؟"
    )

# ============== COMMAND HANDLERS ==============
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_data = get_user_data(user.id)
    
    if not user_data.get('name'):
        user_data['name'] = user.first_name
        save_user_data(user.id, user_data)
    
    await update.message.reply_text(
        f"""✨ أهلاً {user.first_name}!

أنا **Mira** - مساعدك الذكي! 🤖

💬 محادثة ذكية
🎨 إنشاء صور
🎵 إنشاء أغاني
🌐 بحث في الإنترنت
🗣️ رسائل صوتية
💾 أتذكر معلوماتك

اختر من الأزرار:",
        reply_markup=get_main_menu()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🔧 الأوامر:

/start - بدء البوت
/help - المساعدة
/balance - الرصيد
/profile - ملفي
/clear - مسح المحادثة

💡 جرب:
- اكتب أي سؤال
- "ارسم قطة" 🎨
- "ابحث عن ..." 🌐
- "غني لي ..." 🎵
"""
    await update.message.reply_text(help_text)

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = get_user_data(update.message.from_user.id)
    await update.message.reply_text(
        f"💰 رصيدك: {user_data.get('balance', 0)} نقطة\n\n"
        "🎁 يمكنك كسب نقاط أكثر عبر:\n"
        "- دعوة أصدقاء (+30 نقطة)\n"
        "- استخدام البوت بانتظام"
    )

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = get_user_data(update.message.from_user.id)
    
    profile_text = f"""
👤 ملفي الشخصي:

📛 الاسم: {user_data.get('name', 'غير محدد')}
🎂 العمر: {user_data.get('age', 'غير محدد')}
🏙️ المدينة: {user_data.get('city', 'غير محددة')}
❤️ الاهتمامات: {', '.join(user_data.get('interests', [])) or 'غير محددة'}
💰 الرصيد: {user_data.get('balance', 0)} نقطة

➕ لتحديث بياناتي:
- اسمي: [الاسم]
- عمري: [العمر]
- مدينتي: [المدينة]
- اهتمامي: [الاهتمام]
"""
    await update.message.reply_text(profile_text)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.message.from_user.id)
    if user_id in data.get('conversations', {}):
        data['conversations'][user_id] = []
        save_data(data)
    await update.message.reply_text("✅ تم مسح المحادثة! ابدأ من جديد 😊")

# ============== MESSAGE HANDLERS ==============
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    
    # حفظ اسم المستخدم
    user_data = get_user_data(user_id)
    if not user_data.get('name'):
        user_data['name'] = update.message.from_user.first_name
        save_user_data(user_id, user_data)
    
    # معالجة الأوامر الخاصة
    if text.startswith('اسمي:'):
        user_data['name'] = text.replace('اسمي:', '').strip()
        save_user_data(user_id, user_data)
        await update.message.reply_text(f"✅ تم حفظ اسمك: {user_data['name']}")
        return
    
    if text.startswith('عمري:'):
        try:
            user_data['age'] = int(text.replace('عمري:', '').strip())
            save_user_data(user_id, user_data)
            await update.message.reply_text(f"✅ تم حفظ عمرك: {user_data['age']} سنة")
        except:
            await update.message.reply_text("⚠️ اكتب العمر رقماً!")
        return
    
    if text.startswith('مدينتي:'):
        user_data['city'] = text.replace('مدينتي:', '').strip()
        save_user_data(user_id, user_data)
        await update.message.reply_text(f"✅ تم حفظ مدينتك: {user_data['city']}")
        return
    
    if text.startswith('اهتمامي:'):
        interest = text.replace('اهتمامي:', '').strip()
        if interest not in user_data.get('interests', []):
            user_data.setdefault('interests', []).append(interest)
            save_user_data(user_id, user_data)
        await update.message.reply_text(f"✅ تم إضافة الاهتمام: {interest}")
        return
    
    # معالجة الأزرار
    if text == "💬 محادثة":
        await update.message.reply_text(
            "💬 ابدأ محادثة معي! اكتب أي شيء...",
            reply_markup=get_back_menu()
        )
        return
    
    if text == "🎨 رسم":
        await update.message.reply_text(
            "🎨 اكتب وصف الصورة التي تريدها!\n\nمثال: قطة جميلة",
            reply_markup=get_back_menu()
        )
        return
    
    if text == "🎵 أغنية":
        await update.message.reply_text(
            "🎵 اكتب كلمات الأغنية أو وصفها!\n\nمثال: أغنية فرح",
            reply_markup=get_back_menu()
        )
        return
    
    if text == "🌐 بحث":
        await update.message.reply_text(
            "🌐 اكتب ما تريد البحث عنه!\n\nمثال: سعر البيتكوين",
            reply_markup=get_back_menu()
        )
        return
    
    if text == "👤 ملفي":
        await profile_command(update, context)
        return
    
    if text == "💰 رصيدي":
        await balance_command(update, context)
        return
    
    if text == "🔙 رجوع":
        await update.message.reply_text(
            "🔙 رجوع للقائمة",
            reply_markup=get_main_menu()
        )
        return
    
    # معالجة الأوامر الخاصة
    if text.startswith("ارسم ") or text.startswith("draw "):
        prompt = text.replace("ارسم ", "").replace("draw ", "").strip()
        await update.message.reply_text("🎨 جاري إنشاء الصورة...")
        
        image_url = await generate_image(prompt, "anime")
        if image_url:
            await update.message.reply_photo(image_url, caption=f"🎨 {prompt}")
        else:
            await update.message.reply_text(
                f"⚠️ يتطلب OpenAI API لإنشاء الصور\n\n"
                f"الصورة المطلوبة: {prompt}"
            )
        return
    
    if text.startswith("ابحث ") or text.startswith("search "):
        query = text.replace("ابحث ", "").replace("search ", "").strip()
        await update.message.reply_text(f"🔍 جاري البحث عن: {query}")
        
        result = await search_web(query)
        await update.message.reply_text(f"📋 النتيجة:\n\n{result}")
        return
    
    if text.startswith("غني ") or text.startswith("غنية "):
        prompt = text.replace("غني ", "").replace("غنية ", "").strip()
        await update.message.reply_text("🎵 جاري إنشاء الأغنية...")
        
        result = await generate_music(prompt)
        await update.message.reply_text(result)
        return
    
    # محادثة ذكية
    await update.message.reply_text("🤖 جاري التفكير...")
    response = await chat_with_ai(user_id, text)
    await update.message.reply_text(response)

# ============== CALLBACK HANDLERS ==============
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_main":
        await query.message.reply_text(
            "🔙 رجوع للقائمة",
            reply_markup=get_main_menu()
        )
    
    elif query.data.startswith("img_"):
        style = query.data.replace("img_", "")
        await query.message.reply_text(
            f"🎨 اكتب وصف الصورة بـ style {style}:"
        )

# ============== MAIN ==============
def main():
    app = Application.builder()\
        .token(BOT_TOKEN)\
        .build()
    
    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("clear", clear_command))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Set commands
    app.bot.set_my_commands([
        BotCommand("start", "بدء البوت"),
        BotCommand("help", "المساعدة"),
        BotCommand("balance", "رصيدي"),
        BotCommand("profile", "ملفي"),
        BotCommand("clear", "مسح المحادثة"),
    ])
    
    print("🤖 AI Bot يعمل...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()