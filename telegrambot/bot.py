
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

# إعداد Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# افتح الشيت باستخدام Spreadsheet ID (من رابط Google Sheets)
sheet = client.open_by_key("1T8W-GYQx0MZs4RzTQQ64VuZ-rSYCNoh0jAUjmjzka18").sheet1

# رسالة المحتوى
PREDEFINED_MESSAGE = "✅ تم التحقق من إيميلك، هذا هو المحتوى الخاص بك:\nhttps://your-content-link.com"

# أمر /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "السلام عليكم! 👋\nمن فضلك أرسل إيميلك للتحقق من أهليتك للحصول على المحتوى."
    )

# التحقق من الإيميل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().lower()
    all_emails = sheet.col_values(1)

    if user_input in [email.lower() for email in all_emails]:
        row_index = [i for i, email in enumerate(all_emails) if email.lower() == user_input][0] + 1
        status = sheet.cell(row_index, 2).value.strip().lower()
        if status == "no":
            await update.message.reply_text(PREDEFINED_MESSAGE)
            sheet.update_cell(row_index, 2, "Yes")
        else:
            await update.message.reply_text("❌ هذا الإيميل سبق استخدامه، والمحتوى تم إرساله سابقًا.")
    else:
        await update.message.reply_text("❌ الإيميل غير موجود في القائمة.")

# توكن البوت من BotFather
BOT_TOKEN = "8052664239:AAHv2yPhQHH9c0kmFigWnDTi8Mx25py-LAQ"

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
app.run_polling()
