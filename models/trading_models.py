"""
Trading Data Models for #IREKABITI_FX
Pydantic models and dataclasses for trading signals and related data
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import json

class TradingDirection(Enum):
    """Trading direction enumeration"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class MarketType(Enum):
    """Market type enumeration"""
    FOREX = "forex"
    CRYPTO = "crypto"

class SignalStatus(Enum):
    """Signal status enumeration"""
    ACTIVE = "active"
    CLOSED = "closed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class SignalResult(Enum):
    """Signal result enumeration"""
    WIN = "win"
    LOSS = "loss"
    BREAKEVEN = "breakeven"
    PENDING = "pending"

@dataclass
class TradingSignal:
    """Core trading signal model"""
    symbol: str
    direction: str  # BUY, SELL, HOLD
    entry_price: float
    tp_price: float  # Take Profit
    sl_price: float  # Stop Loss
    confidence: int  # 0-100
    timeframe: str
    risk_percent: float
    analysis: str
    timestamp: datetime
    market_type: str  # forex, crypto
    strength: int = 0
    sentiment_score: float = 0.0
    news_impact: float = 0.0
    status: str = "active"
    result: Optional[str] = None
    pnl: Optional[float] = None
    closed_at: Optional[datetime] = None
    signal_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'signal_id': self.signal_id,
            'symbol': self.symbol,
            'direction': self.direction,
            'entry_price': self.entry_price,
            'tp_price': self.tp_price,
            'sl_price': self.sl_price,
            'confidence': self.confidence,
            'timeframe': self.timeframe,
            'risk_percent': self.risk_percent,
            'analysis': self.analysis,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'market_type': self.market_type,
            'strength': self.strength,
            'sentiment_score': self.sentiment_score,
            'news_impact': self.news_impact,
            'status': self.status,
            'result': self.result,
            'pnl': self.pnl,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradingSignal':
        """Create from dictionary"""
        # Convert timestamp strings back to datetime objects
        timestamp = None
        if data.get('timestamp'):
            if isinstance(data['timestamp'], str):
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            else:
                timestamp = data['timestamp']

        closed_at = None
        if data.get('closed_at'):
            if isinstance(data['closed_at'], str):
                closed_at = datetime.fromisoformat(data['closed_at'].replace('Z', '+00:00'))
            else:
                closed_at = data['closed_at']

        return cls(
            signal_id=data.get('signal_id'),
            symbol=data['symbol'],
            direction=data['direction'],
            entry_price=data['entry_price'],
            tp_price=data['tp_price'],
            sl_price=data['sl_price'],
            confidence=data['confidence'],
            timeframe=data['timeframe'],
            risk_percent=data['risk_percent'],
            analysis=data['analysis'],
            timestamp=timestamp,
            market_type=data['market_type'],
            strength=data.get('strength', 0),
            sentiment_score=data.get('sentiment_score', 0.0),
            news_impact=data.get('news_impact', 0.0),
            status=data.get('status', 'active'),
            result=data.get('result'),
            pnl=data.get('pnl'),
            closed_at=closed_at
        )

    def get_risk_reward_ratio(self) -> float:
        """Calculate risk/reward ratio"""
        try:
            risk = abs(self.entry_price - self.sl_price)
            reward = abs(self.tp_price - self.entry_price)
            return reward / risk if risk > 0 else 0
        except:
            return 0

    def get_potential_profit_percent(self) -> float:
        """Calculate potential profit percentage"""
        try:
            return abs((self.tp_price - self.entry_price) / self.entry_price) * 100
        except:
            return 0

    def get_potential_loss_percent(self) -> float:
        """Calculate potential loss percentage"""
        try:
            return abs((self.sl_price - self.entry_price) / self.entry_price) * 100
        except:
            return 0

@dataclass
class SignalConfidence:
    """Signal confidence breakdown"""
    technical_score: float = 0.0
    ml_score: float = 0.0
    sentiment_score: float = 0.0
    news_score: float = 0.0
    overall_confidence: int = 0
    factors: List[str] = field(default_factory=list)

    def calculate_overall(self) -> int:
        """Calculate overall confidence from individual scores"""
        weights = {
            'technical': 0.4,
            'ml': 0.3,
            'sentiment': 0.2,
            'news': 0.1
        }
        
        weighted_score = (
            self.technical_score * weights['technical'] +
            self.ml_score * weights['ml'] +
            self.sentiment_score * weights['sentiment'] +
            self.news_score * weights['news']
        )
        
        self.overall_confidence = max(0, min(100, int(weighted_score)))
        return self.overall_confidence

@dataclass
class MarketData:
    """Market data model"""
    symbol: str
    timeframe: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    market_type: str

@dataclass
class TechnicalIndicators:
    """Technical indicators model"""
    symbol: str
    timeframe: str
    timestamp: datetime
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    atr: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None

@dataclass
class NewsItem:
    """News item model"""
    title: str
    content: str
    source: str
    published_at: datetime
    sentiment_score: float = 0.0
    impact_score: float = 0.0
    symbols: List[str] = field(default_factory=list)
    url: Optional[str] = None
    category: Optional[str] = None

@dataclass
class SentimentData:
    """Sentiment analysis data"""
    symbol: str
    positive: float
    neutral: float
    negative: float
    sentiment_score: float  # -1 to 1
    total_volume: int
    sources: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PortfolioOptimization:
    """Portfolio optimization result"""
    symbols: List[str]
    weights: Dict[str, float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    risk_score: int
    strategy: str
    optimization_timestamp: datetime
    correlation_matrix: Optional[Dict[str, Dict[str, float]]] = None
    monte_carlo: Optional[Dict[str, Any]] = None

@dataclass
class TradingSession:
    """Trading session model"""
    name: str
    start_time: str  # HH:MM format
    end_time: str    # HH:MM format
    timezone: str
    is_active: bool = False

@dataclass
class UserSettings:
    """User settings model"""
    user_id: str
    platform: str  # telegram, discord
    notifications_enabled: bool = True
    min_confidence_threshold: int = 70
    max_daily_signals: int = 10
    preferred_timeframes: List[str] = field(default_factory=lambda: ["1h", "4h"])
    preferred_pairs: List[str] = field(default_factory=list)
    risk_tolerance: str = "medium"  # low, medium, high
    email: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    discord_channel_id: Optional[str] = None

@dataclass
class TradingStats:
    """Trading statistics model"""
    total_signals: int = 0
    successful_signals: int = 0
    win_rate: float = 0.0
    total_return: float = 0.0
    average_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    best_signal: float = 0.0
    worst_signal: float = 0.0
    active_days: int = 0
    average_confidence: float = 0.0
    total_risk_taken: float = 0.0
    profit_factor: float = 0.0
    
    def calculate_win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.total_signals > 0:
            self.win_rate = (self.successful_signals / self.total_signals) * 100
        return self.win_rate

    def calculate_profit_factor(self, total_profit: float, total_loss: float) -> float:
        """Calculate profit factor"""
        if total_loss > 0:
            self.profit_factor = total_profit / abs(total_loss)
        else:
            self.profit_factor = float('inf') if total_profit > 0 else 0
        return self.profit_factor

@dataclass
class BacktestResult:
    """Backtest result model"""
    symbol: str
    start_date: datetime
    end_date: datetime
    total_signals: int
    winning_signals: int
    losing_signals: int
    win_rate: float
    total_return: float
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    average_trade_duration: float  # hours
    best_trade: float
    worst_trade: float
    
@dataclass
class MLPrediction:
    """ML prediction model"""
    symbol: str
    prediction: int  # -1, 0, 1 for sell, hold, buy
    confidence: float
    probabilities: List[float]
    model_type: str
    model_accuracy: float
    features_used: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RiskManagement:
    """Risk management parameters"""
    max_risk_per_trade: float = 2.0  # percentage
    max_daily_risk: float = 6.0      # percentage
    max_portfolio_risk: float = 20.0  # percentage
    stop_loss_multiplier: float = 2.0  # ATR multiplier
    take_profit_multiplier: float = 3.0  # ATR multiplier
    max_correlation: float = 0.7      # maximum correlation between positions
    max_exposure_per_pair: float = 5.0  # percentage
    
    def calculate_position_size(self, account_balance: float, risk_percent: float, 
                              stop_loss_distance: float) -> float:
        """Calculate position size based on risk parameters"""
        try:
            risk_amount = account_balance * (min(risk_percent, self.max_risk_per_trade) / 100)
            return risk_amount / stop_loss_distance if stop_loss_distance > 0 else 0
        except:
            return 0

@dataclass
class MarketScanResult:
    """Market scan result model"""
    scan_timestamp: datetime
    total_pairs_scanned: int
    forex_opportunities: int
    crypto_opportunities: int
    high_confidence_signals: int
    top_opportunities: List[Dict[str, Any]] = field(default_factory=list)
    market_sentiment: str = "neutral"
    session_active: bool = False

@dataclass
class AlertSettings:
    """Alert settings model"""
    signal_alerts: bool = True
    performance_alerts: bool = True
    news_alerts: bool = False
    min_confidence_for_alert: int = 75
    alert_channels: List[str] = field(default_factory=lambda: ["telegram"])
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None    # HH:MM format
    weekend_alerts: bool = False

@dataclass
class SystemHealth:
    """System health status model"""
    timestamp: datetime
    overall_status: str  # healthy, warning, critical
    services_status: Dict[str, str] = field(default_factory=dict)
    api_response_times: Dict[str, float] = field(default_factory=dict)
    error_rates: Dict[str, float] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    last_signal_time: Optional[datetime] = None
    active_connections: int = 0

# Utility functions for model operations

def signal_to_json(signal: TradingSignal) -> str:
    """Convert trading signal to JSON string"""
    return json.dumps(signal.to_dict(), default=str)

def signal_from_json(json_str: str) -> TradingSignal:
    """Create trading signal from JSON string"""
    data = json.loads(json_str)
    return TradingSignal.from_dict(data)

def validate_signal_data(data: Dict[str, Any]) -> List[str]:
    """Validate signal data and return list of errors"""
    errors = []
    
    required_fields = ['symbol', 'direction', 'entry_price', 'tp_price', 'sl_price', 
                      'confidence', 'timeframe', 'market_type']
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate specific field types and ranges
    if 'confidence' in data:
        try:
            confidence = int(data['confidence'])
            if not 0 <= confidence <= 100:
                errors.append("Confidence must be between 0 and 100")
        except (ValueError, TypeError):
            errors.append("Confidence must be a valid integer")
    
    if 'risk_percent' in data:
        try:
            risk = float(data['risk_percent'])
            if not 0 <= risk <= 10:
                errors.append("Risk percent must be between 0 and 10")
        except (ValueError, TypeError):
            errors.append("Risk percent must be a valid number")
    
    if 'direction' in data:
        if data['direction'] not in ['BUY', 'SELL', 'HOLD']:
            errors.append("Direction must be BUY, SELL, or HOLD")
    
    return errors

def create_default_risk_management() -> RiskManagement:
    """Create default risk management settings"""
    return RiskManagement(
        max_risk_per_trade=2.0,
        max_daily_risk=6.0,
        max_portfolio_risk=20.0,
        stop_loss_multiplier=2.0,
        take_profit_multiplier=3.0,
        max_correlation=0.7,
        max_exposure_per_pair=5.0
    )

def create_default_user_settings(user_id: str, platform: str) -> UserSettings:
    """Create default user settings"""
    return UserSettings(
        user_id=user_id,
        platform=platform,
        notifications_enabled=True,
        min_confidence_threshold=70,
        max_daily_signals=10,
        preferred_timeframes=["1h", "4h"],
        preferred_pairs=[],
        risk_tolerance="medium"
    )
