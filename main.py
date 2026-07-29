import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد الـ logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# جلب التوكن
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 مرحباً! بوت التداول يعمل الآن.\n\nأرسل لي صورة لشارت وسأحلله!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 تم استلام الصورة! (التحليل سيضاف لاحقاً)")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if "rsi" in text:
        await update.message.reply_text("📊 RSI: مؤشر القوة النسبية\n- فوق 70 = شراء مفرط\n- تحت 30 = بيع مفرط")
    elif "macd" in text:
        await update.message.reply_text("📊 MACD: مؤشر الاتجاه\n- تقاطع للأعلى = شراء\n- تقاطع للأسفل = بيع")
    else:
        await update.message.reply_text(f"📌 استلمت رسالتك: {text}\n\nاسألني عن RSI أو MACD أو أرسل صورة شارت")

def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN غير موجود!")
        return
    
    logger.info("✅ البوت يبدأ العمل...")
    
    # الطريقة الصحيحة لبناء البوت
    application = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("✅ البوت يعمل!")
    
    # تشغيل البوت
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
