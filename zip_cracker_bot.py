import os
import shutil
import pyzipper
import py7zr
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

BOT_TOKEN = "8080301293:AAFwfN8Vk7tJfB_xHTvgjMRERp5EmUcvTLw"

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 *Welcome User!*\nSend your password protected `.zip` or `.7z` file.", parse_mode="Markdown")

# Handle both .zip and .7z files
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    file_name = file.file_name.lower()

    if not file_name.endswith((".zip", ".7z")):
        await update.message.reply_text("❌ Only .zip and .7z files are supported.")
        return

    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{file.file_id}_{file_name}"
    file_obj = await context.bot.get_file(file.file_id)
    await file_obj.download_to_drive(file_path)

    await update.message.reply_text("📥 Got it! Now wait a min, I am cracking your file 🔓")

    # Crack password
    password = crack_file(file_path)

    if password:
        await update.message.reply_text(f"✅ *Password Found:* `{password}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Sorry, password not found in range 000–999.")

    # Clean up
    shutil.rmtree("unzipped", ignore_errors=True)
    os.remove(file_path)

# Detect and crack file type
def crack_file(file_path):
    if file_path.endswith(".zip"):
        return crack_zip(file_path)
    elif file_path.endswith(".7z"):
        return crack_7z(file_path)
    return None

# Crack .zip using pyzipper
def crack_zip(zip_path):
    os.makedirs("unzipped", exist_ok=True)
    for i in range(1000):
        password = f"{i:03}"
        try:
            with pyzipper.AESZipFile(zip_path) as zf:
                zf.pwd = password.encode('utf-8')
                zf.extractall("unzipped/")
                return password
        except:
            continue
    return None

# Crack .7z using py7zr
def crack_7z(sevenz_path):
    os.makedirs("unzipped", exist_ok=True)
    for i in range(1000):
        password = f"{i:03}"
        try:
            with py7zr.SevenZipFile(sevenz_path, mode='r', password=password) as archive:
                archive.extractall(path="unzipped/")
                return password
        except:
            continue
    return None

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
