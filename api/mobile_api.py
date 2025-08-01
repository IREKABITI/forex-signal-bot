"""
Mobile API for #IREKABITI_FX
FastAPI backend for mobile app companion
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import asyncio
import json
from datetime import datetime, timedelta
import jwt
import os

from services.signal_generator import SignalGenerator
from services.portfolio_optimizer import PortfolioOptimizer
from database.db_manager import DatabaseManager
from services.market_data import MarketDataService
from models.trading_models import TradingSignal
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger()

# Initialize FastAPI app
app = FastAPI(
    title="#IREKABITI_FX Mobile API",
    description="AI-Powered Multi-Market Trading Ecosystem Mobile API",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "irekabiti_fx_secret_key_2024")

# Services
signal_generator = SignalGenerator()
portfolio_optimizer = PortfolioOptimizer()
db_manager = DatabaseManager()
market_data = MarketDataService()

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                await self.disconnect(connection)

manager = ConnectionManager()

# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str

class SignalRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"

class PortfolioRequest(BaseModel):
    symbols: Optional[List[str]] = None
    
class NotificationSettings(BaseModel):
    push_notifications: bool = True
    email_notifications: bool = False
    min_confidence: int = 70

# Authentication
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Routes

@app.get("/", response_class=HTMLResponse)
async def mobile_app(request: Request):
    """Serve mobile app interface"""
    return templates.TemplateResponse("mobile_app.html", {"request": request})

@app.post("/auth/login")
async def login(user_data: UserLogin):
    """User authentication"""
    try:
        # Simple authentication - in production, use proper user management
        if user_data.username == "admin" and user_data.password == os.getenv("ADMIN_PASSWORD", "admin123"):
            token_data = {
                "sub": user_data.username,
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "expires_in": 86400,
                "user": {
                    "username": user_data.username,
                    "role": "admin"
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@app.get("/api/signals/latest")
async def get_latest_signals(limit: int = 10, username: str = Depends(verify_token)):
    """Get latest trading signals"""
    try:
        signals = await signal_generator.get_latest_signals(limit)
        return {
            "success": True,
            "data": signals,
            "count": len(signals),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting latest signals: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch signals")

@app.post("/api/signals/generate")
async def generate_signal(request: SignalRequest, username: str = Depends(verify_token)):
    """Generate signal for specific symbol"""
    try:
        signal = await signal_generator.generate_signal(request.symbol, request.timeframe)
        
        if signal:
            # Broadcast new signal to connected clients
            await manager.broadcast({
                "type": "new_signal",
                "data": {
                    "symbol": signal.symbol,
                    "direction": signal.direction,
                    "confidence": signal.confidence,
                    "entry_price": signal.entry_price,
                    "timestamp": signal.timestamp.isoformat()
                }
            })
            
            return {
                "success": True,
                "data": {
                    "symbol": signal.symbol,
                    "direction": signal.direction,
                    "entry_price": signal.entry_price,
                    "tp_price": signal.tp_price,
                    "sl_price": signal.sl_price,
                    "confidence": signal.confidence,
                    "risk_percent": signal.risk_percent,
                    "analysis": signal.analysis,
                    "timeframe": signal.timeframe
                }
            }
        else:
            return {
                "success": False,
                "message": "No signal generated - conditions not met"
            }
            
    except Exception as e:
        logger.error(f"Error generating signal: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate signal")

@app.get("/api/market/scan")
async def scan_markets(username: str = Depends(verify_token)):
    """Scan all markets for opportunities"""
    try:
        scan_results = await signal_generator.scan_all_markets()
        return {
            "success": True,
            "data": scan_results
        }
    except Exception as e:
        logger.error(f"Error scanning markets: {e}")
        raise HTTPException(status_code=500, detail="Failed to scan markets")

@app.get("/api/portfolio/optimize")
async def optimize_portfolio(symbols: Optional[str] = None, username: str = Depends(verify_token)):
    """Optimize portfolio allocation"""
    try:
        symbol_list = symbols.split(",") if symbols else None
        optimization = await portfolio_optimizer.optimize_portfolio(symbol_list)
        
        return {
            "success": optimization.get("success", False),
            "data": optimization
        }
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize portfolio")

@app.get("/api/analytics/performance")
async def get_performance_analytics(days: int = 30, username: str = Depends(verify_token)):
    """Get performance analytics"""
    try:
        # Get signal performance stats
        signal_stats = await signal_generator.get_signal_performance_stats()
        
        # Get trading stats from database
        trading_stats = await db_manager.get_trading_stats()
        
        # Get daily report
        daily_report = await db_manager.get_daily_report()
        
        return {
            "success": True,
            "data": {
                "signal_stats": signal_stats,
                "trading_stats": trading_stats,
                "daily_report": daily_report,
                "period_days": days
            }
        }
    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

@app.get("/api/market/prices")
async def get_market_prices(symbols: str, username: str = Depends(verify_token)):
    """Get current market prices"""
    try:
        symbol_list = symbols.split(",")
        prices = {}
        
        for symbol in symbol_list:
            market_type = "crypto" if symbol.endswith("USDT") else "forex"
            price = await market_data.get_current_price(symbol, market_type)
            if price:
                prices[symbol] = price
                
        return {
            "success": True,
            "data": prices,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting market prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch prices")

@app.get("/api/backtest")
async def run_backtest(days: int = 30, username: str = Depends(verify_token)):
    """Run signal backtest"""
    try:
        backtest_results = await signal_generator.backtest_signal_accuracy(days)
        return {
            "success": True,
            "data": backtest_results
        }
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        raise HTTPException(status_code=500, detail="Failed to run backtest")

@app.get("/api/news/summary")
async def get_news_summary(symbols: Optional[str] = None, username: str = Depends(verify_token)):
    """Get news summary"""
    try:
        from services.news_service import NewsService
        news_service = NewsService()
        
        symbol_list = symbols.split(",") if symbols else None
        news_data = await news_service.get_cached_news(symbol_list)
        
        return {
            "success": True,
            "data": {
                "articles": news_data.get("articles", [])[:10],
                "analysis": news_data.get("analysis", {})
            }
        }
    except Exception as e:
        logger.error(f"Error getting news summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news")

@app.get("/api/sentiment/analysis")
async def get_sentiment_analysis(symbols: str, username: str = Depends(verify_token)):
    """Get sentiment analysis for symbols"""
    try:
        from services.sentiment_analysis import SentimentAnalysis
        sentiment_service = SentimentAnalysis()
        
        symbol_list = symbols.split(",")
        sentiment_data = await sentiment_service.get_market_sentiment_summary(symbol_list)
        
        return {
            "success": True,
            "data": sentiment_data
        }
    except Exception as e:
        logger.error(f"Error getting sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sentiment")

@app.get("/api/dashboard/summary")
async def get_dashboard_summary(username: str = Depends(verify_token)):
    """Get dashboard summary data"""
    try:
        # Get recent signals
        recent_signals = await signal_generator.get_latest_signals(5)
        
        # Get performance stats
        performance = await signal_generator.get_signal_performance_stats()
        
        # Get market status
        market_status = await market_data.get_market_status()
        
        # Get active trading session
        from config.settings import settings
        active_session = "London" if 8 <= datetime.utcnow().hour < 17 else "New York" if 13 <= datetime.utcnow().hour < 22 else "Closed"
        
        return {
            "success": True,
            "data": {
                "recent_signals": recent_signals,
                "performance": performance,
                "market_status": market_status,
                "active_session": active_session,
                "total_pairs": len(settings.TRADING_PAIRS_FOREX + settings.TRADING_PAIRS_CRYPTO),
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(30)  # Send update every 30 seconds
            
            # Get latest signal
            recent_signals = await signal_generator.get_latest_signals(1)
            if recent_signals:
                await websocket.send_text(json.dumps({
                    "type": "signal_update",
                    "data": recent_signals[0]
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "market_data": "active",
            "signal_generator": "active",
            "database": "active",
            "ml_analysis": "active"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        await db_manager.initialize()
        logger.info("🚀 #IREKABITI_FX Mobile API started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        await market_data.close_connections()
        logger.info("👋 #IREKABITI_FX Mobile API shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return {"error": "Endpoint not found", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return {"error": "Internal server error", "status_code": 500}
