import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from langchain.agents import create_agent
from features.users.service import AuthService
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.messages import HumanMessage
from config.db import client

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
                  "When displaying products, always include the product 'image_url' in your response as a markdown image.\n"
                  "Be polite and professional and don't return response in markdown format just plain text, except for the image.\n"
                  "IMPORTANT: Remember context from the conversation. If the user mentions their size, preferences, or other details, use that information to answer follow-up questions.",
)

def get_session_history(session_id: str):
    return MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string=os.getenv("MONGODB_URL"),
        database_name="salesmate",
        collection_name="chat_history",
    )

async def process_chat(session_id: str, user_text: str):
    history = get_session_history(session_id)
    current_messages = history.messages
    
    user_msg = HumanMessage(content=user_text)
    
    input_messages = current_messages + [user_msg]
    
    response = await agent.ainvoke({"messages": input_messages})
    
    all_messages = response["messages"]
    
    new_messages = all_messages[len(current_messages):]
    
    await history.aadd_messages(new_messages)
    
    return all_messages[-1].content

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Welcome to SalesMate! 🛍️\n\n"
        "Here are the things I can help you with:\n\n"
        "👤 Account Actions:\n"
        "1. /register \"Full Name\" <mobile> <email> <password> - Create a new account\n"
        "2. /login <email> <password> - Login to your account\n\n"
        "🛒 Shopping:\n"
        "- Ask me about our latest products (e.g., 'Show me men's t-shirts')\n"
        "- Check prices and availability\n"
        "- View product images\n\n"
        "ℹ️ Help:\n"
        "- /help - Show this menu again"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Here are the available commands:\n\n"
        "/start - Start the conversation and see the main menu\n"
        "/register \"Name\" <mobile> <email> <password> - Register a new user\n"
        "/login <email> <password> - Login to the system\n"
        "/help - Show this help message\n\n"
        "You can also ask me natural language questions like:\n"
        "- \"What dresses do you have?\"\n"
        "- \"Show me jackets under $100\"\n"
        "- \"Do you have canvas sneakers?\""
    )
    await update.message.reply_text(help_text)

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

from langchain_core.messages import HumanMessage

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    session_id = str(update.effective_chat.id)

    response_content = await process_chat(session_id, user_text)

    try:
        await update.message.reply_text(response_content, parse_mode='Markdown')
    except Exception:
        await update.message.reply_text(response_content)
    
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started. Polling...")
    app.run_polling()