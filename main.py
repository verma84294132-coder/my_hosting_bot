import os, threading, subprocess, time
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)
@app.route('/')
def home():
    return "👑 Hosting Bot Live Hai! 🔥"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

running_bots = {}
os.makedirs("hosted", exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📂 File Bhejo / Upload Bot", callback_data="upload")],
        [InlineKeyboardButton("📊 My Bots", callback_data="mybots")],
        [InlineKeyboardButton("🛑 Sab Stop Karo", callback_data="stop_all")],
        [InlineKeyboardButton("💎 Premium Hosting", callback_data="premium")],
    ]
    await update.message.reply_text(
        "👑 **PREMIUM HOSTING BOT** 💎\n\n"
        "🔥 Ab Koi Bhi Bot Yahi Se Host Karo 🔥\n\n"
        "✨ **Kaise Use Kare?**\n"
        "1️⃣ Apni `.py` file bhejo 📂\n"
        "2️⃣ Main usko RUN kar dunga 🚀\n"
        "3️⃣ /mybots se status dekho 📊\n"
        "4️⃣ /stop se band karo 🛑\n\n"
        "⚡ Fast • 💎 Premium • 🔥 24x7",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "upload":
        await query.edit_message_text("📂 **FILE BHEJO BOSS** ✨\n\nApni `.py` wali bot file yahi bhej do 👇\n\n⚠️ File me BOT_TOKEN pehle se hona chahiye!", parse_mode="Markdown")
    elif query.data == "mybots":
        uid = query.from_user.id
        if uid not in running_bots:
            await query.edit_message_text("😔 **Koi Bot Run Nahi Hai**\n\n📂 Pehle file bhejo!", parse_mode="Markdown")
        else:
            info = running_bots[uid]
            status = "🟢 RUNNING" if info['process'].poll() is None else "🔴 STOPPED"
            await query.edit_message_text(f"📊 **MY BOTS** 💎\n\n📁 File: `{info['filename']}`\n📡 Status: {status}", parse_mode="Markdown")
    elif query.data == "stop_all":
        uid = query.from_user.id
        if uid in running_bots:
            try: running_bots[uid]['process'].terminate()
            except: pass
            del running_bots[uid]
            await query.edit_message_text("🛑 **Bot Stop Ho Gaya!** ✅", parse_mode="Markdown")
        else:
            await query.edit_message_text("😔 Koi bot run hi nahi ho raha!", parse_mode="Markdown")
    elif query.data == "premium":
        await query.edit_message_text("💎 **PREMIUM HOSTING** 💎\n\n✅ ⚡ Super Fast Server\n✅ 📂 Unlimited File Upload\n✅ 🔥 Auto Restart\n✅ 👑 24x7 Online", parse_mode="Markdown")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    doc = update.message.document
    if not doc or not doc.file_name.endswith(".py"):
        await update.message.reply_text("❌ Bhai sirf `.py` file bhejo! 📂")
        return
    await update.message.reply_text(f"📥 **File Mil Gayi!** `{doc.file_name}`\n\n⏳ Ab Run Kar Raha Hu... 🚀", parse_mode="Markdown")
    if uid in running_bots:
        try: running_bots[uid]['process'].terminate()
        except: pass
    file = await context.bot.get_file(doc.file_id)
    save_path = f"hosted/{uid}_{doc.file_name}"
    await file.download_to_drive(save_path)
    try:
        process = subprocess.Popen(["python", save_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        running_bots[uid] = {'process': process, 'filename': doc.file_name, 'time': time.strftime("%I:%M %p")}
        await update.message.reply_text(f"🔥 **BOT LIVE HO GAYA!** 🔥\n\n📁 File: `{doc.file_name}`\n📡 Status: 🟢 RUNNING\n\n📊 /mybots\n🛑 /stop", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")

async def mybots_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in running_bots:
        await update.message.reply_text("😔 Koi bot run nahi hai. Pehle file bhejo 📂")
        return
    info = running_bots[uid]
    status = "🟢 RUNNING" if info['process'].poll() is None else "🔴 STOPPED"
    await update.message.reply_text(f"📊 **MY BOT**\n\n📁 `{info['filename']}`\n📡 {status}", parse_mode="Markdown")

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in running_bots:
        try: running_bots[uid]['process'].terminate()
        except: pass
        del running_bots[uid]
        await update.message.reply_text("🛑 **Bot Stop Ho Gaya!** ✅")
    else:
        await update.message.reply_text("😔 Koi bot run hi nahi hai!")

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("mybots", mybots_cmd))
    app_bot.add_handler(CommandHandler("stop", stop_cmd))
    app_bot.add_handler(CallbackQueryHandler(button_handler))
    app_bot.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    print("👑 Hosting Bot Started... 🔥")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
