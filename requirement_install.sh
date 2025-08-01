#!/bin/bash

# #IREKABITI_FX Trading Ecosystem Installation Script
# AI-Powered Multi-Market Trading Platform

set -e

echo "🚀 Installing #IREKABITI_FX Trading Ecosystem"
echo "============================================="

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.8 or higher is required. Found version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv irekabiti_fx_env

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source irekabiti_fx_env/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
python -m pip install --upgrade pip

# Install core Python packages
echo "📚 Installing core Python packages..."
pip install fastapi uvicorn python-multipart

# Data science and ML packages
echo "🤖 Installing ML and data science packages..."
pip install numpy pandas scikit-learn tensorflow transformers
pip install scipy matplotlib seaborn plotly

# Technical analysis
echo "📊 Installing technical analysis packages..."
pip install TA-Lib || echo "⚠️  TA-Lib installation failed. Installing alternative..."
pip install pandas-ta

# Trading and market data
echo "💹 Installing trading packages..."
pip install MetaTrader5 python-binance alpha-vantage yfinance

# Bot frameworks
echo "🤖 Installing bot frameworks..."
pip install python-telegram-bot discord.py

# Sentiment analysis and NLP
echo "🧠 Installing NLP packages..."
pip install tweepy praw nltk textblob

# News and data sources
echo "📰 Installing news API packages..."
pip install newsapi-python

# Database and async
echo "🗄️  Installing database packages..."
pip install aiosqlite sqlalchemy alembic

# Web and API
echo "🌐 Installing web packages..."
pip install aiohttp requests

# Scheduling and async tasks
echo "⏰ Installing scheduling packages..."
pip install schedule apscheduler

# Utilities
echo "🛠️  Installing utility packages..."
pip install python-dotenv pydantic pyjwt
pip install pytz dateutil

# Development and testing (optional)
echo "🧪 Installing development packages..."
pip install pytest pytest-asyncio black flake8

# Additional financial packages
echo "💰 Installing additional financial packages..."
pip install quantlib || echo "⚠️  QuantLib installation failed (optional)"

# Ensure uvicorn is installed (fix for container error)
echo "⚡ Ensuring uvicorn is installed and available..."
pip install uvicorn --force-reinstall

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p data logs models static templates config

# Create environment file template with embedded credentials
echo "📄 Creating environment configuration..."
cat > .env.example << EOF
# #IREKABITI_FX Configuration Template
# Copy this file to .env and fill in your API keys

# Bot Tokens (already filled in for deployment)
TELEGRAM_TOKEN=8123034561:AAFUmL-YVT2uybFNDdl4U9eKQtz2w1f1dPo
TELEGRAM_CHAT_ID=5689209090
DISCORD_WEBHOOK=https://discord.com/api/webhooks/1398658870980644985/0fHPvafJv0Bi6uc0RzPITEzcKgqKt6znfhhrBy-4qFBas8BfxiTxjyFkVqtp_ctt-Ndt

# Market Data APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key

# MetaTrader 5 (if using)
MT5_LOGIN=your_mt5_login
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_mt5_server

# News API
NEWS_API_KEY=your_newsdata_io_key

# Social Media APIs
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_SECRET=your_reddit_secret

# Admin Configuration
ADMIN_TELEGRAM_IDS=5689209090
ADMIN_DISCORD_IDS=123456789,987654321
ADMIN_PASSWORD=your_admin_password

# JWT Secret for mobile API
JWT_SECRET_KEY=your_jwt_secret_key

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
EOF

# Create startup script
echo "🚀 Creating startup script..."
cat > start.sh << 'EOF'
#!/bin/bash
# #IREKABITI_FX Startup Script

echo "🚀 Starting #IREKABITI_FX Trading Ecosystem"

# Check if virtual environment exists
if [ ! -d "irekabiti_fx_env" ]; then
    echo "❌ Virtual environment not found. Please run requirements_install.sh first."
    exit 1
fi

# Activate virtual environment
source irekabiti_fx_env/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure your API keys."
    exit 1
fi

# Start the application
python main.py
EOF

chmod +x start.sh

# Create service worker for PWA
echo "📱 Creating service worker for PWA..."
mkdir -p static
cat > static/sw.js << 'EOF'
const CACHE_NAME = 'irekabiti-fx-v1';
const urlsToCache = [
  '/',
  '/static/styles.css',
  '/static/app.js',
  '/static/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});
EOF

# Create PWA manifest
cat > static/manifest.json << 'EOF'
{
  "name": "#IREKABITI_FX - AI Trading Platform",
  "short_name": "IREKABITI_FX",
  "description": "AI-Powered Multi-Market Trading Ecosystem",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1a1a1a",
  "theme_color": "#00ff88",
  "icons": [
    {
      "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>",
      "sizes": "192x192",
      "type": "image/svg+xml"
    }
  ]
}
EOF

# Create systemd service file (for Linux servers)
echo "⚙️  Creating systemd service file..."
cat > irekabiti-fx.service << EOF
[Unit]
Description=#IREKABITI_FX AI Trading Ecosystem
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/irekabiti_fx_env/bin
ExecStart=$(pwd)/irekabiti_fx_env/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "🎉 Installation Complete!"
echo "========================"
echo ""
echo "📋 Next Steps:"
echo "1. Copy .env.example to .env and configure your API keys if needed"
echo "2. Run: ./start.sh to start the application"
echo ""
echo "🔧 Optional Setup:"
echo "- To install as system service: sudo cp irekabiti-fx.service /etc/systemd/system/"
echo "- Then: sudo systemctl enable irekabiti-fx.service"
echo "- Start service: sudo systemctl start irekabiti-fx.service"
echo ""
echo "📚 Documentation:"
echo "- Telegram Bot: Already configured with token and chat ID"
echo "- Discord Bot/Webhook: Already configured"
echo "- MetaTrader 5: Install MT5 terminal and configure login"
echo "- Binance: Get API key from Binance"
echo "- Alpha Vantage: Get free API key from alphavantage.co"
echo ""
echo "🚀 #IREKABITI_FX is ready to trade!"
echo "Elite AI-powered signals await you!"

# Check if TA-Lib installation was successful
python3 -c "import talib" 2>/dev/null && echo "✅ TA-Lib installed successfully" || echo "⚠️  TA-Lib not installed - using pandas-ta alternative"

echo ""
echo "💡 Pro Tip: Run 'python -c \"import MetaTrader5; print(MetaTrader5.__version__)\"' to verify MT5 package"

deactivate
