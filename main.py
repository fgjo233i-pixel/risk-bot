import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from PIL import Image
import io

# إعداد السجلات
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# المتغيرات
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# إنشاء عميل OpenAI
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

# لوحة المفاتيح الرئيسية
def get_main_keyboard():
    keyboard = [
        [KeyboardButton(" تحليل صورة"), KeyboardButton(" نصيحة تداول")],
        [KeyboardButton("📈 اتجاه السوق"), KeyboardButton("❓ مساعدة")],
        [KeyboardButton("🔧 الإعدادات"), KeyboardButton(" المؤشرات")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# أمر البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
👋 *مرحباً بك في بوت التداول الذكي!*

أنا هنا لمساعدتك في:
📊 تحليل الشارتات والصور
💡 تقديم نصائح تداول
📈 تحليل اتجاهات السوق
📚 شرح المؤشرات الفنية

*اختر من القائمة أو أرسل لي:*
- صورة لشارت وسأحلله
- سؤال عن التداول
- أي استفسار آخر

للبداية، اضغط على أحد الأزرار في الأسفل 👇
    """
    await update.message.reply_text(
        welcome_text, 
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# تحليل الصورة
async def analyze_image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 *أرسل لي صورة الشارت الآن وسأقوم بتحليلها*",
        parse_mode='Markdown'
    )

# معالجة الصور
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("🔄 جاري تحليل الصورة... انتظر لحظة")
        
        # الحصول على الصورة
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        photo_bytes = await file.download_as_bytearray()
        
        if not OPENAI_API_KEY:
            await update.message.reply_text(
                "⚠️ لم يتم إعداد مفتاح OpenAI بعد.\n"
                "يرجى إضافة OPENAI_API_KEY في متغيرات Railway"
            )
            return
        
        # تحليل الصورة باستخدام OpenAI Vision
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """أنت خبير تحليل فني في التداول. 
                    حلل الشارت المرسل وقدم:
                    1. الاتجاه العام (صاعد/هابط/جانبي)
                    2. مستويات الدعم والمقاومة
                    3. المؤشرات الظاهرة
                    4. توصية واضحة (شراء/بيع/انتظار)
                    5. نقاط الدخول والخروج المقترحة
                    
                    كن دقيقاً ومختصراً."""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "حلل هذا الشارت للتداول"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{photo_bytes[:1000000].hex()}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
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
            "❌ حدث خطأ في تحليل الصورة. تأكد من:\n"
            "- وضوح الصورة\n"
            "- وجود مفتاح OpenAI صحيح\n"
            "جرب إرسال صورة أخرى"
        )

# نصيحة تداول عشوائية
async def trading_tip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tips = [
        "💡 *نصيحة:* لا تستثمر أكثر مما تستطيع تحمل خسارته",
        "💡 *نصيحة:* استخدم وقف الخسارة دائماً لحماية رأس مالك",
        "💡 *نصيحة:* لا تتبع السوق بعواطفك، التزم بخطتك",
        "💡 *نصيحة:* التنويع يقلل المخاطر",
        "💡 *نصيحة:* تعلم من خسائرك كما تتعلم من أرباحك"
    ]
    import random
    await update.message.reply_text(
        random.choice(tips),
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# اتجاه السوق
async def market_trend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📈 *لتحليل اتجاه السوق، أرسل لي:* \n"
        "- اسم الزوج/العملة (مثل: BTC/USD, EUR/USD)\n"
        "- أو أرسل صورة شارت وسأحلله",
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# المساعدة
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 *كيفية استخدام البوت:*

*1️⃣ تحليل الصور:*
- اضغط "تحليل صورة"
- أرسل صورة شارت واضحة
- سأقوم بتحليله فورياً

*2️ الأسئلة:*
- اسألني أي سؤال عن التداول
- المؤشرات، الاستراتيجيات، إلخ

*3️⃣ الأزرار:*
- استخدم الأزرار في الأسفل للوصول السريع

*ملاحظات مهمة:*
⚠️ تحليلاتي ليست نصيحة مالية
⚠️ تداول بمسؤولية
⚠️ دائماً استخدم وقف الخسارة
    """
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# المؤشرات
async def indicators(update: Update, context: ContextTypes.DEFAULT_TYPE):
    indicators_text = """
 *المؤشرات الفنية الشائعة:*

*1. RSI (مؤشر القوة النسبية):*
- فوق 70 = شراء مفرط
- تحت 30 = بيع مفرط

*2. MACD:*
- تقاطع الخط الصاعد = إشارة شراء
- تقاطع الخط الهابط = إشارة بيع

*3. Moving Averages:*
- السعر فوق المتوسط = اتجاه صاعد
- السعر تحت المتوسط = اتجاه هابط

*4. Bollinger Bands:*
- لمس الحد العلوي = مقاومة
- لمس الحد السفلي = دعم

*لشرح أي مؤشر، اسألني عنه!*
    """
    await update.message.reply_text(
        indicators_text,
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# معالجة النصوص
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    # الردود السريعة
    if "rsi" in text:
        await update.message.reply_text(
            "📊 *RSI (مؤشر القوة النسبية):*\n"
            "يقيس قوة الزخم السعري.\n\n"
            "• فوق 70 = الشراء مفرط (احتمال هبوط)\n"
            "• تحت 30 = البيع مفرط (احتمال صعود)\n"
            "• بين 30-70 = منطقة متعادلة",
            parse_mode='Markdown'
        )
    elif "macd" in text:
        await update.message.reply_text(
            "📊 *MACD:*\n"
            "مؤشر اتجاه ومتابعة للاتجاه.\n\n"
            "• تقاطع خط MACD للأعلى = شراء\n"
            "• تقاطع خط MACD للأسفل = بيع\n"
            "• الابتعاد عن خط الصفر = قوة الاتجاه",
            parse_mode='Markdown'
        )
    elif "متوسط" in text or "moving average" in text:
        await update.message.reply_text(
            "📊 *المتوسطات المتحركة:*\n\n"
            "SMA 50: متوسط 50 يوم\n"
            "SMA 200: متوسط 200 يوم\n\n"
            "• السعر فوق المتوسط = دعم\n"
            "• السعر تحت المتوسط = مقاومة\n"
            "• تقاطع 50 مع 200 = إشارة قوية",
            parse_mode='Markdown'
        )
    else:
        # رد عام
        await update.message.reply_text(
            " *سؤال جيد!*\n\n"
            "لأساعدك بشكل أفضل، يمكنك:\n"
            "1. إرسال صورة شارت للتحليل\n"
            "2. السؤال عن مؤشر محدد (RSI, MACD, إلخ)\n"
            "3. طلب نصيحة تداول\n\n"
            "استخدم الأزرار في الأسفل للوصول السريع!",
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )

# معالجة الأخطاء
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception while handling an update: {context.error}")

# الدالة الرئيسية
def main() -> None:
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found! Please add it to environment variables")
        return
    
    logger.info("✅ Starting bot...")
    
    # إنشاء التطبيق
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(60)
        .build()
    )
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # معالجات الأزرار
    application.add_handler(MessageHandler(
        filters.Regex("^📊 تحليل صورة$"), 
        analyze_image_command
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
        filters.Regex("^❓ مساعدة$"), 
        help_command
    ))
    application.add_handler(MessageHandler(
        filters.Regex("^📚 المؤشرات$"), 
        indicators
    ))
    
    # معالج الأخطاء
    application.add_error_handler(error_handler)
    
    logger.info("✅ Bot is running!")
    
    # تشغيل البوت
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
