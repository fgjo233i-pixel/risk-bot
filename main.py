import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
import base64
from io import BytesIO

# إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# المتغيرات
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# إنشاء عميل OpenAI إذا كان المفتاح موجوداً
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

# لوحة المفاتيح الرئيسية
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("📊 تحليل شارت"), KeyboardButton("💡 نصيحة تداول")],
        [KeyboardButton("📈 اتجاه السوق"), KeyboardButton("📚 المؤشرات")],
        [KeyboardButton("️ الإعدادات"), KeyboardButton("❓ مساعدة")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# لوحة المفاتيح للمؤشرات
def get_indicators_keyboard():
    keyboard = [
        [KeyboardButton("RSI"), KeyboardButton("MACD")],
        [KeyboardButton("المتوسطات"), KeyboardButton("Bollinger")],
        [KeyboardButton("🔙 رجوع")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# أمر البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
 *مرحباً بك في بوت التداول الذكي!*

أنا مساعدك الشخصي للتحليل الفني والتداول.

*ما يمكنني فعله:*
📊 تحليل الشارتات بالذكاء الاصطناعي
 تقديم نصائح تداول يومية
 تحليل اتجاهات السوق
 شرح المؤشرات الفنية
⚙️ إعدادات مخصصة

*للبداية:*
- أرسل صورة لشارت وسأحلله
- استخدم الأزرار في الأسفل
- أو اسألني أي سؤال عن التداول

*ملاحظة مهمة:*
⚠️ تحليلاتي ليست نصيحة مالية
️ تداول بمسؤولية دائماً
    """
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# تحليل الشارت (زر)
async def analyze_chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 *أرسل لي صورة الشارت الآن*\n\n"
        "سأقوم بتحليله باستخدام الذكاء الاصطناعي وإعطائك:\n"
        "• الاتجاه العام\n"
        "• مستويات الدعم والمقاومة\n"
        "• نقاط الدخول والخروج\n"
        "• التوصية (شراء/بيع/انتظار)",
        parse_mode='Markdown'
    )

# معالجة الصور
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not OPENAI_API_KEY:
        await update.message.reply_text(
            "⚠️ *لم يتم إعداد OpenAI بعد*\n\n"
            "يرجى إضافة OPENAI_API_KEY في متغيرات Railway",
            parse_mode='Markdown'
        )
        return
    
    try:
        await update.message.reply_text("🔄 جاري تحليل الصورة... انتظر لحظة 📊")
        
        # الحصول على الصورة
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        photo_bytes = await file.download_as_bytearray()
        
        # تحويل الصورة إلى base64
        photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
        
        # تحليل الصورة باستخدام OpenAI Vision
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """أنت خبير تحليل فني محترف في تداول الأسهم والعملات والكريبتو.
                    مهمتك تحليل الشارت المرسل بدقة وتقديم:
                    
                    1. *الاتجاه العام:* (صاعد قوي/صاعد ضعيف/هابط قوي/هابط ضعيف/جانبي)
                    2. *المستويات الرئيسية:* (الدعم والمقاومة)
                    3. *الأنماط الظاهرة:* (مثلث، علم، رأس وكتفين، إلخ)
                    4. *المؤشرات المرئية:* (إذا كانت ظاهرة)
                    5. *التوصية:* (شراء/بيع/انتظار) مع نسبة الثقة
                    6. *نقاط الدخول والخروج المقترحة*
                    7. *وقف الخسارة المقترح*
                    
                    كن دقيقاً ومختصراً ومنظماً في الإجابة."""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "حلل هذا الشارت للتداول وأعطِ توصية واضحة"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{photo_base64[:4000000]}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=800
        )
        
        analysis = response.choices[0].message.content
        
        # إرسال التحليل
        await update.message.reply_text(
            f" *نتيجة التحليل:*\n\n{analysis}",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error analyzing photo: {e}")
        await update.message.reply_text(
            "❌ *حدث خطأ في التحليل*\n\n"
            "الأسباب المحتملة:\n"
            "• الصورة غير واضحة\n"
            "• مشكلة في مفتاح OpenAI\n"
            "• خطأ تقني مؤقت\n\n"
            "جرب إرسال صورة أخرى أو تحقق من جودة الصورة",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )

# نصيحة تداول
async def trading_tip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tips = [
        ("📊 *إدارة المخاطر:*\n"
         "لا تخاطر بأكثر من 1-2% من رأس مالك في صفقة واحدة.\n"
         "هذا يحميك من الخسائر الكبيرة."),
        
        ("🎯 *وقف الخسارة:*\n"
         "دائماً استخدم وقف الخسارة قبل الدخول في الصفقة.\n"
         "لا تؤجله أبداً!"),
        
        ("📈 *الاتجاه صديقك:*\n"
         "تداول مع الاتجاه العام وليس ضده.\n"
         "الاتجاه هو أقوى مؤشر!"),
        
        ("🧘 *التحكم العاطفي:*\n"
         "لا تتبع السوق بعواطفك.\n"
         "التزم بخطتك المكتوبة."),
        
        ("⏰ *الصبر:*\n"
         "90% من التداول هو انتظار.\n"
         "انتظر الفرص المثالية ولا تستعجل."),
        
        ("📚 *التعلم المستمر:*\n"
         "السوق يتطور دائماً.\n"
         "استمر في التعلم والتحسين."),
        
        ("💰 *حجم المركز:*\n"
         "لا تدخل صفقة كبيرة جداً.\n"
         "وزع مخاطر على عدة صفقات."),
        
        ("📊 *التنويع:*\n"
         "لا تضع كل أموالك في أصل واحد.\n"
         "نوِّع لتقليل المخاطر.")
    ]
    
    import random
    tip = random.choice(tips)
    
    await update.message.reply_text(
        tip,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# اتجاه السوق
async def market_trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trend_text = """
📈 *تحليل اتجاه السوق*

*لتحليل اتجاه سوق معين، أرسل لي:*
• اسم الزوج أو العملة (مثل: BTC/USD)
• أو أرسل صورة شارت وسأحلله

*أو اسألني عن:*
• RSI - لمعرفة حالة التشبع
• MACD - لتحليل الاتجاه
• المتوسطات المتحركة
• أو أي مؤشر آخر

💡 *نصيحة:* 
الاتجاه الصاعد: السعر فوق المتوسط 50 و 200
الاتجاه الهابط: السعر تحت المتوسط 50 و 200
    """
    
    await update.message.reply_text(
        trend_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# المؤشرات
async def indicators(update: Update, context: ContextTypes.DEFAULT_TYPE):
    indicators_text = """
📚 *المؤشرات الفنية الشائعة:*

*1️ RSI (مؤشر القوة النسبية)*
• فوق 70 = شراء مفرط (احتمال هبوط)
• تحت 30 = بيع مفرط (احتمال صعود)
• 50 = منطقة متعادلة

*2️⃣ MACD*
• تقاطع خط MACD للأعلى = شراء
• تقاطع خط MACD للأسفل = بيع
• الابتعاد عن الصفر = قوة الاتجاه

*3️⃣ المتوسطات المتحركة*
• SMA 50: متوسط 50 يوم
• SMA 200: متوسط 200 يوم
• السعر فوق المتوسط = دعم
• السعر تحت المتوسط = مقاومة

*4️⃣ Bollinger Bands*
• اللمس العلوي = مقاومة
• اللمس السفلي = دعم
• الانقباض = استعداد لحركة قوية

*5️ حجم التداول*
• حجم عالي = تأكيد الاتجاه
• حجم منخفض = ضعف الاتجاه

*لاستفسار عن أي مؤشر، اسألني!*
    """
    
    await update.message.reply_text(
        indicators_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# المساعدة
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 *كيفية استخدام البوت:*

*📊 تحليل الصور:*
1. اضغط "تحليل شارت"
2. أرسل صورة شارت واضحة
3. انتظر التحليل (5-10 ثواني)

*💬 الأسئلة:*
• اسأل عن أي مؤشر (RSI, MACD, إلخ)
• اسأل عن استراتيجيات التداول
• اسأل عن إدارة المخاطر

*📈 المعلومات:*
• اتجاه السوق
• نصائح يومية
• شرح المؤشرات

*⚙️ الإعدادات:*
(قريباً - تخصيص الإشعارات)

*أزرار القائمة:*
استخدم الأزرار في الأسفل للوصول السريع!

*ملاحظات مهمة:*
️ التحليل ليس نصيحة مالية
⚠️ تداول بمسؤولية
⚠️ استخدم وقف الخسارة دائماً
    """
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# الإعدادات
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings_text = """
⚙️ *الإعدادات*

*الإعدادات الحالية:*
• اللغة: العربية ✅
• التحليل: مفعل ✅
• الإشعارات: قريباً

*قريباً:*
 إشعارات الأسعار
 تقارير يومية
🎯 تخصيص المؤشرات
⏰ تنبيهات الصفقات

*للتواصل والدعم:*
راسلني لأي استفسار أو اقتراح!
    """
    
    await update.message.reply_text(
        settings_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# معالجة النصوص
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    # الردود المخصصة
    if "rsi" in text:
        await update.message.reply_text(
            "📊 *RSI - مؤشر القوة النسبية*\n\n"
            "*المفهوم:*\n"
            "يقيس قوة الزخم السعري وسرعة تغيره\n\n"
            "*القراءة:*\n"
            "• فوق 70 = شراء مفرط (احتمال هبوط)\n"
            "• تحت 30 = بيع مفرط (احتمال صعود)\n"
            "• بين 30-70 = منطقة متعادلة\n\n"
            "*استراتيجية التداول:*\n"
            "• RSI > 70: فكر في البيع\n"
            "• RSI < 30: فكر في الشراء\n"
            "• RSI = 50: اتجاه محايد",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    elif "macd" in text:
        await update.message.reply_text(
            "📊 *MACD - مؤشر التقارب والاختلاف*\n\n"
            "*المفهوم:*\n"
            "يظهر العلاقة بين متوسطين متحركين\n\n"
            "*المكونات:*\n"
            "• خط MACD (الأزرق)\n"
            "• خط الإشارة (الأحمر)\n"
            "• الهيستوجرام (الأعمدة)\n\n"
            "*الإشارات:*\n"
            "• تقاطع للأعلى = شراء \n"
            "• تقاطع للأسفل = بيع 🔴\n"
            "• الابتعاد عن الصفر = قوة الاتجاه",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    elif "متوسط" in text or "average" in text or "moving" in text:
        await update.message.reply_text(
            "📊 *المتوسطات المتحركة*\n\n"
            "*SMA (بسيط):*\n"
            "• SMA 50: متوسط 50 يوم\n"
            "• SMA 200: متوسط 200 يوم\n\n"
            "*EMA (أسي):*\n"
            "• يعطي وزن أكبر للأسعار الحديثة\n\n"
            "*الاستخدام:*\n"
            "• السعر فوق المتوسط = دعم 🟢\n"
            "• السعر تحت المتوسط = مقاومة 🔴\n"
            "• تقاطع 50 مع 200 = إشارة قوية",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    elif "bollinger" in text or "بولنجر" in text:
        await update.message.reply_text(
            "📊 *Bollinger Bands - نطاق بولينجر*\n\n"
            "*المكونات:*\n"
            "• الخط الأوسط: SMA 20\n"
            "• الحد العلوي: +2 انحراف معياري\n"
            "• الحد السفلي: -2 انحراف معياري\n\n"
            "*الإشارات:*\n"
            "• لمس الحد العلوي = مقاومة\n"
            "• لمس الحد السفلي = دعم\n"
            "• انقباض النطاق = استعداد لحركة قوية",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    elif "وقف" in text or "stop" in text or "loss" in text:
        await update.message.reply_text(
            "🛡️ *وقف الخسارة*\n\n"
            "*لماذا مهم:*\n"
            "• يحمي رأس مالك من الخسائر الكبيرة\n"
            "• يزيل العاطفة من التداول\n"
            "• يحدد المخاطرة مسبقاً\n\n"
            "*كيف تحدده:*\n"
            "• تحت آخر قاع مهم\n"
            "• نسبة 2-3% من السعر\n"
            "• عند مستوى دعم/مقاومة",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    elif "شراء" in text or "بيع" in text or "توصية" in text:
        await update.message.reply_text(
            "💡 *نصائح للتوصيات:*\n\n"
            "⚠️ أنا لا أقدم توصيات مباشرة\n"
            "لكن يمكنني مساعدتك في:\n\n"
            " تحليل الشارتات\n"
            "📚 شرح المؤشرات\n"
            "💡 تقديم نصائح عامة\n\n"
            "*تذكر:*\n"
            "• اتخذ قراراتك بنفسك\n"
            "• استخدم وقف الخسارة\n"
            "• لا تخاطر بأكثر مما تتحمل",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    elif "رجوع" in text or "🔙" in text:
        await update.message.reply_text(
            "🔙 *العودة للقائمة الرئيسية*",
            reply_markup=get_main_keyboard()
        )
    
    else:
        await update.message.reply_text(
            f"📌 *رسالتك:* {update.message.text}\n\n"
            "💡 *يمكنني مساعدتك في:*\n"
            "• تحليل الشارتات (أرسل صورة)\n"
            "• شرح المؤشرات (RSI, MACD, إلخ)\n"
            "• نصائح التداول\n"
            "• معلومات عن السوق\n\n"
            "استخدم الأزرار في الأسفل! 👇",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )

# معالجة الأخطاء
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception while handling an update: {context.error}")

# الدالة الرئيسية
def main() -> None:
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found!")
        logger.error("Please add it to Railway Variables")
        return
    
    logger.info("✅ Starting Trading Bot...")
    
    # إنشاء التطبيق
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(60)
        .pool_timeout(60)
        .build()
    )
    
    # معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # معالجات الأزرار
    application.add_handler(MessageHandler(
        filters.Regex("^📊 تحليل شارت$"), 
        analyze_chart_command
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^💡 نصيحة تداول$"), 
        trading_tip
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^📈 اتجاه السوق$"), 
        market_trend
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^📚 المؤشرات$"), 
        indicators
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^️ الإعدادات$"), 
        settings
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^❓ مساعدة$"), 
        help_command
    ))
    
    # معالجات الرسائل
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # معالج الأخطاء
    application.add_error_handler(error_handler)
    
    logger.info("✅ Bot is running!")
    
    # تشغيل البوت
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
