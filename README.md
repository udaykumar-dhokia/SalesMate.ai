# SalesMate.ai

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Python-green?style=flat&logo=langchain&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google_Gemini-LLM-yellow?style=flat&logo=google&logoColor=white)

**SalesMate.ai** is an intelligent Telegram-based sales agent designed for fashion brands. It leverages the power of Large Language Models (LLM) to understand natural language queries, manage user sessions, and search product inventory seamlessly.

## System Architecture

The following diagram illustrates the high-level architecture of SalesMate.ai:

```mermaid
graph TD
    User((User)) <-->|Messages| Telegram[Telegram Bot]
    Telegram <-->|Updates| Agent[Main Agent Logic]
    Agent <-->|Memory| History[Mongo Memory]

    subgraph Core System
        Agent <-->|Content Generation| LLM[Google Gemini LLM]
        Agent <-->|User Auth| Auth[Auth Service]
        Agent <-->|Inventory Search| InvTools[Inventory Tool]
        Agent <-->|Place Orders| OrderTool[Order Tool]

        InvTools <-->|Query| Inv[Inventory Service]
        OrderTool -->|Create| Orders[Order Service]
        OrderTool -->|Notify| Email[Email Service]
    end

    subgraph Data Layer
        Auth <-->|Users| DB[(MongoDB)]
        Inv <-->|Products| DB
        Orders <-->|Orders| DB
        History <-->|Chat Logs| DB
    end

    Email -.->|SMTP| User

    style User fill:#f9f,stroke:#333
    style DB fill:#ee7,stroke:#333
```

## Features

- **Secure Authentication**: Register and login securely via Telegram commands.
- **Natural Language Search**: Ask vague questions like "Show me some summer dresses" and get precise results.
- **Visual Shopping**: View product images directly within the chat for a better shopping experience.
- **Conversational Memory**: The bot remembers your preferences and context (e.g., size), allowing for seamless follow-up questions.
- **Order System**: "Buy" products directly in the chat. The bot calculates totals, creates orders, and simulates payments.
- **Real-time Notifications**: Receive professional HTML email confirmations with order details via SMTP.
- **Contextual AI**: Uses Google's Gemini-1.5-flash for understanding user intent and context.

## Workflows

### 1. User Registration & Login Flow

Users must authenticate to link their Telegram account with the system.

```mermaid
sequenceDiagram
    participant User
    participant Bot as Telegram Bot
    participant Auth as Auth Service
    participant DB as MongoDB

    Note over User, Bot: Registration
    User->>Bot: /register "John Doe" +12345 user@email.com pass
    Bot->>Auth: create_user(email, pass, name, mobile)
    Auth->>DB: Check if exists
    Auth->>Auth: Hash Password (bcrypt)
    Auth->>DB: Insert User
    DB-->>Bot: Success (User ID)
    Bot-->>User: "Registration successful!"

    Note over User, Bot: Login
    User->>Bot: /login user@email.com pass
    Bot->>Auth: authenticate_user(email, pass)
    Auth->>DB: Fetch User
    Auth-->>Bot: User Object (if valid)

    alt Credentials Valid
        Bot->>Auth: link_telegram_id(email, chat_id)
        Auth->>DB: Update Telegram ID
        Bot-->>User: "Login successful!"
    else Invalid
        Bot-->>User: "Invalid email or password."
    end
```

### 2. Inventory Search Flow

The AI Agent autonomously decides when to query the database based on user messages.

```mermaid
flowchart LR
    User[User Message] -->|Input| Agent

    subgraph "Reasoning Engine"
        Agent{Intent?}
        Agent -->|Chit-chat| Reply[Direct Reply]
        Agent -->|Product Query| Tool[Call 'search_inventory']
    end

    Tool -->|Parameters| Service[Inventory Service]
    Service -->|Regex Search| DB[(MongoDB)]
    DB -->|Results| Service
    Service -->|JSON Data| Tool

    Tool -->|Context| Agent
    Agent -->|Natural Language Response| User

    style User fill:#cef,stroke:#333
    style Agent fill:#afa,stroke:#333
    style DB fill:#ee7,stroke:#333
```

### 3. Order & Payment Flow

Seamlessly buy products and receive email confirmations.

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant OrderService
    participant EmailService

    User->>Agent: "I want to buy 2 T-Shirts"
    Agent->>Agent: Check Inventory & Calculate Total

    alt Email Missing
        Agent->>User: "What is your email?"
        User->>Agent: "user@example.com"
    end

    Agent->>OrderService: create_order(items, total)
    OrderService-->>Agent: Order Created (ID, PaymentID)

    Agent->>EmailService: send_confirmation(email, order)
    EmailService->>User: Send HTML Email (SMTP)

    Agent-->>User: "Payment Successful! Order #123 placed."
```

## Setup & Installation

### Prerequisites

- Python 3.9+
- MongoDB Instance (Local or Atlas)
- Telegram Bot Token (from @BotFather)
- Gemini API Key
- SMTP Credentials (for emails)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/udaykumar-dhokia/SalesMate.ai.git
   cd SalesMate.ai/agent
   ```

2. **Install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   Create a `.env` file in the `agent` directory:

   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token
   GEMINI_API_KEY=your_gemini_key
   MONGODB_URL=mongodb://localhost:27017/

   # SMTP Configuration (Gmail Example)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

4. **Seed Database**
   Populate the database with dummy data:

   ```bash
   python scripts/seed_inventory.py
   ```

5. **Run the Bot**
   ```bash
   python main.py
   ```

### Docker Support

Alternatively, you can run the entire system (Agent + MongoDB) using Docker.

1.  **Build and Run**:

    ```bash
    docker-compose up --build
    ```

    The bot will start, and MongoDB will be available automatically.

## Tech Stack

- **Language**: Python 3.13
- **LLM Framework**: LangChain & LangGraph
- **Model**: Google Gemini 1.5 Flash
- **Database**: MongoDB
- **Interface**: Python Telegram Bot
