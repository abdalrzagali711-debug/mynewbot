import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# تفعيل تسجيل الأخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# قراءة التوكن من Environment Variable
TOKEN = os.environ.get("TOKEN2")
if not TOKEN:
    raise ValueError("يرجى تعيين توكن البوت كمتغير بيئة باسم TOKEN2")

# ========================
# خدمة 1: أمر /start مع الترحيب باسم المستخدم
# ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"مرحبًا {user_name}! 👋\nالبوت شغال 24 ساعة على Render.")

# ========================
# خدمة 2: إزالة خلفية الصور (RemBG)
# ========================
from rembg import remove
from io import BytesIO
from PIL import Image

async def remove_bg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("يرجى إرسال صورة.")
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_bytes = await file.download_as_bytearray()
    
    output = remove(file_bytes)
    bio = BytesIO(output)
    bio.name = "output.png"
    bio.seek(0)

    await update.message.reply_photo(photo=bio, caption="تمت إزالة الخلفية ✅")

# ========================
# خدمة 3: تحويل نص إلى صورة
# ========================
from PIL import ImageDraw, ImageFont

async def text_to_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith("/"):
        return

    img = Image.new('RGB', (500, 300), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    d.text((10, 10), text, fill=(0,0,0), font=font)

    bio = BytesIO()
    img.save(bio, format='PNG')
    bio.name = "text.png"
    bio.seek(0)

    await update.message.reply_photo(photo=bio, caption="تم تحويل النص إلى صورة ✅")

# ========================
# خدمة 4: عد الكلمات والأحرف
# ========================
async def count_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text or text.startswith("/"):
        return

    num_words = len(text.split())
    num_chars = len(text)

    await update.message.reply_text(
        f"عدد الكلمات: {num_words}\nعدد الأحرف: {num_chars}"
    )

# ========================
# إعداد التطبيق وتشغيله
# ========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, remove_bg))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, count_text))

    app.run_polling()

if __name__ == "__main__":
    main()
