import os
import pyzipper
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
import shutil

BOT_TOKEN = "8080301293:AAFwfN8Vk7tJfB_xHTvgjMRERp5EmUcvTLw"
  # <-- Paste your token here

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 *Welcome User!*\nSend Your Password Protected Zip File", parse_mode="Markdown")

# When user sends ZIP file
async def handle_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if not file.file_name.endswith(".zip"):
        await update.message.reply_text("❌ Please send a .zip file only.")
        return

    # Download ZIP
    file_path = f"downloads/{file.file_id}.zip"
    os.makedirs("downloads", exist_ok=True)
    new_file = await context.bot.get_file(file.file_id)
    await new_file.download_to_drive(file_path)

    await update.message.reply_text("📥 Got it! Now wait a min, I am cracking your zip 🔓")

    # Crack ZIP
    password = crack_zip(file_path)

    if password:
        await update.message.reply_text(f"✅ *Password Found:* `{password}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Sorry, password not found in range 000-999.")

    # Clean up
    shutil.rmtree("unzipped", ignore_errors=True)
    os.remove(file_path)

# Cracking logic
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

# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_zip))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
