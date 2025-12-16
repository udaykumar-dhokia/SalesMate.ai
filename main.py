import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from langchain.agents import create_agent
from features.users.service import AuthService

from tools.inventory_tools import search_inventory

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
)
agent = create_agent(
    model=model,
    tools=[search_inventory],
    system_prompt="You are a helpful sales assistant for SalesMate, a fashion brand.\n"
                  "You can check our inventory to answer user questions about products, prices, and availability.\n"
                  "If a user asks about products, use the 'search_inventory' tool to find relevant items.\n" 
                  "Be polite and professional and don't return response in markdown format just plain text.",
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to SalesMate!\n\n 1) /register 'Full Name' <mobile> <email> <password>\n 2) /login <email> <password>")

auth_service = AuthService()

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    
    if len(args) < 4:
        await update.message.reply_text('Usage: /register "Full Name" <mobile> <email> <password>')
        return
    
    
    if len(args) >= 4:
        mobile_number = args[-3]
        email = args[-2]
        password = args[-1]
        full_name = " ".join(args[:-3])
    else:
        await update.message.reply_text('Usage: /register "Full Name" <mobile> <email> <password>')
        return

    try:
        user_id = auth_service.create_user(email, password, full_name, mobile_number, telegram_chat_id=update.effective_chat.id)
        await update.message.reply_text(f"Registration successful! User ID: {user_id}")
    except ValueError as e:
        await update.message.reply_text(str(e))
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Usage: /login <email> <password>")
        return
        
    email, password = args
    user = auth_service.authenticate_user(email, password)
    if user:
        auth_service.link_telegram_id(email, update.effective_chat.id)
        await update.message.reply_text("Login successful!")
    else:
        await update.message.reply_text("Invalid email or password.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    response_state = agent.invoke({"messages": [("user", user_text)]})
    response_content = response_state["messages"][-1].text
    await update.message.reply_text(response_content)
    
app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("register", register))
app.add_handler(CommandHandler("login", login))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot started. Polling...")
app.run_polling()