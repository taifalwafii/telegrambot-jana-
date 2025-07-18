import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    ConversationHandler, filters
)

# --------- إعداد Google Sheets ---------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1T8W-GYQx0MZs4RzTQQ64VuZ-rSYCNoh0jAUjmjzka18").sheet1

# --------- تعريف الحالات ---------
EMAIL, COURSE, OPTIONAL_2 = range(3)

# --------- محتوى الكورسات ---------
COURSE_CONTENT = {
    "1": """🔓 رابط الوصول لمحتوى دورة AutoCAD:

https://t.me/+sH5T-OJY3-IyYWE0

📢 رابط القناة: https://t.me/+rjKahVZkk0cyODRk

💬 رابط القروب: https://t.me/+eLZh4mI7JdNhNjFk

⚠️ ملاحظة: لا تشارك هذا الرابط أو الإيميل مع أي شخص، النظام يستخدم بوت ذكي سيمنع تكرار الدخول وسيُعتبر خرقًا للحقوق.

شكرًا لاشتراكك في دورة AutoCAD من Jana Studio""",

    "2": """🔓 D5 Render رابط الوصول لمحتوى دورة :

https://t.me/+hc7rLVxgT_s4NzZk

📢 رابط القناة: https://t.me/+nK3PttqkPng1ZjA0

💬 رابط القروب: https://t.me/+k3jBsUpI4vhmOWNk

⚠️ ملاحظة: لا تشارك هذا الرابط أو الإيميل مع أي شخص، النظام يستخدم بوت ذكي سيمنع تكرار الدخول وسيُعتبر خرقًا للحقوق.

شكرًا لاشتراكك في دورة D5 Render
من Jana Studio"""
}

# --------- /start ---------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("السلام عليكم! 👋\nمن فضلك أرسل إيميلك للتحقق.")
    return EMAIL

# --------- التحقق من الإيميل ---------
async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip().lower()
    all_emails = sheet.col_values(1)

    if email in [e.lower() for e in all_emails]:
        row = [i for i, e in enumerate(all_emails) if e.lower() == email][0] + 1
        context.user_data["row"] = row
        await update.message.reply_text(
            "⚠️ الرجاء كتابة رقم الدورة المشترك بها:\n\n"
            "🔹 اضغط رقم 1 إذا كنت مشتركًا في دورة “AutoCAD”\n\n"
            "🔹 اضغط رقم 2 إذا كنت مشتركًا في دورة “D5 Render”\n\n"
            "—\nJana Studio"
        )
        return COURSE
    else:
        await update.message.reply_text(
            "❌ لم يتم العثور على هذا الإيميل في قائمة المشتركين.\n\n"
            "تأكد من أنك كتبت الإيميل بالشكل الصحيح تمامًا كما استخدمته عند الشراء.\n\n"
            "إذا كنت متأكد أنك اشتريت الدورة، تواصل معنا على الخاص للمساعدة.\n\n"
            "—\nJana Studio"
        )
        return EMAIL

# --------- معالجة رقم الكورس ---------
async def handle_course_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    course = update.message.text.strip()
    if course not in ["1", "2"]:
        await update.message.reply_text("⚠️ الرجاء كتابة رقم الدورة بشكل صحيح: 1 أو 2 فقط.")
        return COURSE

    row = context.user_data["row"]
    col_map = {"1": 2, "2": 3}

    cell_value = sheet.cell(row, col_map[course]).value
    if not cell_value or cell_value.strip() == "":
        await update.message.reply_text(
            f"❌ لم يتم العثور على اشتراكك في هذه الدورة (رقم {course}).\n\n"
            "يرجى التأكد أنك اشتركت في الدورة قبل طلب المحتوى.\n\n"
            "إذا كنت تواجه مشكلة أو تعتقد أن هذا خطأ، تواصل معنا عبر الخاص للمساعدة.\n\n"
            "—\nJana Studio"
        )
        return COURSE

    status = cell_value.strip().lower()
    if status == "yes":
        await update.message.reply_text(
            "⚠️ تم استخدام هذا الإيميل مسبقًا وارسال محتوى هذه الدورة.\n\n"
            "نظامنا لا يسمح بتكرار إرسال المحتوى لنفس المستخدم لحماية الحقوق.\n\n"
            "إذا كنت تقصد دورة رقم 2 الرجاء إعادة الإرسال.\n\n"
            "إذا كنت تواجه مشكلة أو تعتقد أن هذا خطأ، تواصل معنا عبر الخاص للمساعدة.\n\n"
            "—\nJana Studio"
        )
        return COURSE
    else:
        await update.message.reply_text(COURSE_CONTENT[course])
        sheet.update_cell(row, col_map[course], "Yes")

        if course == "1":
            await update.message.reply_text("هل ترغب بالحصول على كورس آخر أيضًا؟ الرجاء إرسال الرقم.")
            return OPTIONAL_2
        else:
            await update.message.reply_text("يمكنك كتابة /cancel لإنهاء المحادثة أو طلب كورس آخر.")
            return COURSE

# --------- معالجة كورس 2 الاختياري ---------
async def handle_optional_course2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    course = update.message.text.strip()
    if course != "2":
        await update.message.reply_text("❌ يرجى إرسال رقم دورة غير مستخدمة أو /cancel لإنهاء المحادثة.")
        return OPTIONAL_2

    row = context.user_data["row"]
    cell_value = sheet.cell(row, 3).value
    if not cell_value or cell_value.strip() == "":
        await update.message.reply_text(
            f"❌ لم يتم العثور على اشتراكك في هذه الدورة (رقم 2).\n\n"
            "يرجى التأكد أنك اشتركت في الدورة قبل طلب المحتوى.\n\n"
            "إذا كنت تواجه مشكلة أو تعتقد أن هذا خطأ، تواصل معنا عبر الخاص للمساعدة.\n\n"
            "—\nJana Studio"
        )
        return OPTIONAL_2

    status = cell_value.strip().lower()
    if status == "yes":
        await update.message.reply_text("⚠️ تم استخدام هذا الإيميل مسبقًا وارسال محتوى هذه الدورة.")
    else:
        await update.message.reply_text(COURSE_CONTENT["2"])
        sheet.update_cell(row, 3, "Yes")

    await update.message.reply_text("إذا أردت شيئًا آخر أرسل رقم كورس، أو /cancel لإنهاء المحادثة.")
    return COURSE

# --------- إنهاء يدوي ---------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ تم إنهاء المحادثة. يمكنك البدء من جديد بكتابة /start.")
    return ConversationHandler.END

# --------- إعداد البوت ---------
BOT_TOKEN = "8052664239:AAHv2yPhQHH9c0kmFigWnDTi8Mx25py-LAQ"

app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email)],
        COURSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_course_choice)],
        OPTIONAL_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_optional_course2)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    conversation_timeout=1800,  # 30 دقيقة
)

app.add_handler(conv_handler)
app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, cancel))
app.run_polling()
