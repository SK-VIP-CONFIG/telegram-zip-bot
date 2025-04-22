import os
import pyzipper
import py7zr
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("8080301293:AAFwfN8Vk7tJfB_xHTvgjMRERp5EmUcvTLw")

# Crack ZIP using pyzipper (AES compatible)
def crack_zip(file_path):
    for pwd in range(0, 1000):
        try:
            with pyzipper.AESZipFile(file_path) as zf:
                zf.pwd = str(pwd).zfill(3).encode()
                zf.extractall(path="extracted_zip/")
            return str(pwd).zfill(3)
        except:
            continue
    return None

# Crack .7z files using py7zr
def crack_7z(file_path):
    for pwd in range(0, 1000):
        try:
            with py7zr.SevenZipFile(file_path, mode='r', password=str(pwd).zfill(3)) as archive:
                archive.extractall(path="extracted_7z/")
            return str(pwd).zfill(3)
        except:
            continue
    return None

# Determine file type and crack accordingly
def crack_file(file_path):
    if file_path.endswith(".zip"):
        return crack_zip(file_path)
    elif file_path.endswith(".7z"):
        return crack_7z(file_path)
    else:
        return None

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome User!\n\n📁 Send your password protected `.zip` or `.7z` file.\n✅I will try to crack the password using 000–999.\n✅Password Must Have Under 0-999")

# When user sends file
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if not file.file_name.endswith((".zip", ".7z")):
        await update.message.reply_text("❌ Only .zip and .7z files are supported.")
        return

    await update.message.reply_text("✅ Got your file! Cracking in progress... Please wait ⏳")
    file_path = f"downloads/{file.file_name}"
    os.makedirs("downloads", exist_ok=True)

    # Download file
    file_obj = await file.get_file()
    await file_obj.download_to_drive(file_path)

    # Crack password
    password = crack_file(file_path)

    if password:
        await update.message.reply_text(f"🔐 Password found: `{password}`", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Password not found in range 000–999.")

# Main function
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
