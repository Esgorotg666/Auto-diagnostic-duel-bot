import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import random

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Sample question database
QUESTIONS = [
    {"question": "What does OBD-II code P0300 mean?", "options": ["Random/multiple cylinder misfire", "Throttle position sensor failure", "Catalyst efficiency below threshold", "EVAP leak detected"], "answer": 0},
    {"question": "A weak ground connection can cause what electrical issue?", "options": ["High voltage", "Parasitic drain", "Voltage drop", "Open circuit"], "answer": 2},
    {"question": "If an alternator is undercharging, what is a likely symptom?", "options": ["Engine overheating", "Dim lights", "ABS failure", "Low tire pressure warning"], "answer": 1},
    {"question": "What is the normal cranking voltage range for a healthy 12V battery?", "options": ["6-8V", "9.6-10.5V", "12.6-13.2V", "14.5-15.5V"], "answer": 1},
    {"question": "Which sensor most directly affects fuel trim?", "options": ["MAP sensor", "Crankshaft position sensor", "O2 sensor", "Knock sensor"], "answer": 2}
]

# Game state
QUIZ, ANSWER = range(2)
user_scores = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔧 Welcome to Auto Diagnostic Duel!\nType /play to start a solo quiz."
    )

async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data['score'] = 0
    context.user_data['q_index'] = 0
    context.user_data['questions'] = random.sample(QUESTIONS, 5)
    return await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q_index = context.user_data['q_index']
    question_data = context.user_data['questions'][q_index]
    reply_markup = ReplyKeyboardMarkup([[opt] for opt in question_data['options']], one_time_keyboard=True)
    await update.message.reply_text(f"❓ Q{q_index+1}: {question_data['question']}", reply_markup=reply_markup)
    return ANSWER

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text
    q_index = context.user_data['q_index']
    question_data = context.user_data['questions'][q_index]
    correct_option = question_data['options'][question_data['answer']]

    if user_answer == correct_option:
        context.user_data['score'] += 1
        await update.message.reply_text("✅ Correct!")
    else:
        await update.message.reply_text(f"❌ Wrong! Correct answer: {correct_option}")

    context.user_data['q_index'] += 1
    if context.user_data['q_index'] >= 5:
        score = context.user_data['score']
        await update.message.reply_text(f"🏁 Quiz complete! Your score: {score}/5")
        return ConversationHandler.END
    else:
        return await send_question(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Game cancelled.")
    return ConversationHandler.END

def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    quiz_handler = ConversationHandler(
        entry_points=[CommandHandler("play", play)],
        states={
            ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(quiz_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
