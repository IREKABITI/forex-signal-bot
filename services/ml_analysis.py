"""
Machine Learning Analysis Service for #IREKABITI_FX
Implements pattern recognition and ML-based signal enhancement
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from typing import Dict, List, Tuple, Optional
from utils.logger import setup_logger

logger = setup_logger()

class MLAnalysis:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.model_path = "models/"
        self.ensure_model_directory()
        
    def ensure_model_directory(self):
        """Ensure model directory exists"""
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
            
    def prepare_features(self, data: pd.DataFrame, indicators: Dict) -> pd.DataFrame:
        """Prepare features for ML model"""
        try:
            features = pd.DataFrame(index=data.index)
            
            # Price-based features
            features['price_change'] = data['Close'].pct_change()
            features['high_low_ratio'] = data['High'] / data['Low']
            features['volume_change'] = data['Volume'].pct_change()
            
            # Technical indicator features
            if 'RSI' in indicators and not indicators['RSI'].empty:
                features['rsi'] = indicators['RSI']
                features['rsi_oversold'] = (indicators['RSI'] < 30).astype(int)
                features['rsi_overbought'] = (indicators['RSI'] > 70).astype(int)
                
            if 'MACD' in indicators and not indicators['MACD'].empty:
                features['macd'] = indicators['MACD']
                features['macd_signal'] = indicators['Signal']
                features['macd_histogram'] = indicators['Histogram']
                features['macd_bullish'] = (indicators['MACD'] > indicators['Signal']).astype(int)
                
            if 'ATR' in indicators and not indicators['ATR'].empty:
                features['atr'] = indicators['ATR']
                features['atr_normalized'] = indicators['ATR'] / data['Close']
                
            # Bollinger Bands features
            if 'Upper' in indicators and not indicators['Upper'].empty:
                features['bb_position'] = (data['Close'] - indicators['Lower']) / (indicators['Upper'] - indicators['Lower'])
                features['bb_squeeze'] = ((indicators['Upper'] - indicators['Lower']) / indicators['Middle'])
                
            # Moving Average features
            if 'SMA_20' in indicators:
                sma_20 = pd.Series(indicators['SMA_20'], index=data.index)
                features['price_vs_sma20'] = data['Close'] / sma_20
                features['above_sma20'] = (data['Close'] > sma_20).astype(int)
                
            if 'SMA_50' in indicators:
                sma_50 = pd.Series(indicators['SMA_50'], index=data.index)
                features['price_vs_sma50'] = data['Close'] / sma_50
                features['above_sma50'] = (data['Close'] > sma_50).astype(int)
                
            # Volatility features
            features['volatility_5'] = data['Close'].rolling(5).std()
            features['volatility_20'] = data['Close'].rolling(20).std()
            
            # Momentum features
            features['momentum_5'] = data['Close'] / data['Close'].shift(5) - 1
            features['momentum_10'] = data['Close'] / data['Close'].shift(10) - 1
            
            # Candlestick features
            features['candle_size'] = abs(data['Close'] - data['Open']) / data['Open']
            features['upper_shadow'] = (data['High'] - np.maximum(data['Open'], data['Close'])) / data['Open']
            features['lower_shadow'] = (np.minimum(data['Open'], data['Close']) - data['Low']) / data['Open']
            features['is_bullish'] = (data['Close'] > data['Open']).astype(int)
            
            # Time-based features
            features['hour'] = data.index.hour
            features['day_of_week'] = data.index.dayofweek
            
            # Drop NaN values
            features = features.dropna()
            
            self.feature_columns = features.columns.tolist()
            return features
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return pd.DataFrame()
            
    def create_labels(self, data: pd.DataFrame, lookahead: int = 5, threshold: float = 0.001) -> pd.Series:
        """Create labels for supervised learning"""
        try:
            labels = []
            
            for i in range(len(data) - lookahead):
                current_price = data['Close'].iloc[i]
                future_price = data['Close'].iloc[i + lookahead]
                
                price_change = (future_price - current_price) / current_price
                
                if price_change > threshold:
                    labels.append(1)  # Buy signal
                elif price_change < -threshold:
                    labels.append(-1)  # Sell signal
                else:
                    labels.append(0)  # Hold signal
                    
            # Pad with neutral labels
            labels.extend([0] * lookahead)
            
            return pd.Series(labels, index=data.index)
            
        except Exception as e:
            logger.error(f"Error creating labels: {e}")
            return pd.Series()
            
    def train_model(self, symbol: str, data: pd.DataFrame, indicators: Dict) -> bool:
        """Train ML model for a specific symbol"""
        try:
            logger.info(f"Training ML model for {symbol}")
            
            # Prepare features and labels
            features = self.prepare_features(data, indicators)
            labels = self.create_labels(data)
            
            if features.empty or labels.empty:
                logger.error(f"No valid features or labels for {symbol}")
                return False
                
            # Align features and labels
            common_index = features.index.intersection(labels.index)
            features = features.loc[common_index]
            labels = labels.loc[common_index]
            
            if len(features) < 100:  # Minimum samples required
                logger.error(f"Insufficient data for training {symbol}: {len(features)} samples")
                return False
                
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=42, stratify=labels
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train Random Forest model
            rf_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            rf_model.fit(X_train_scaled, y_train)
            
            # Train Gradient Boosting model
            gb_model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42
            )
            gb_model.fit(X_train_scaled, y_train)
            
            # Evaluate models
            rf_pred = rf_model.predict(X_test_scaled)
            gb_pred = gb_model.predict(X_test_scaled)
            
            rf_accuracy = accuracy_score(y_test, rf_pred)
            gb_accuracy = accuracy_score(y_test, gb_pred)
            
            logger.info(f"RF Accuracy for {symbol}: {rf_accuracy:.3f}")
            logger.info(f"GB Accuracy for {symbol}: {gb_accuracy:.3f}")
            
            # Choose best model
            if rf_accuracy >= gb_accuracy:
                best_model = rf_model
                model_type = "RandomForest"
            else:
                best_model = gb_model
                model_type = "GradientBoosting"
                
            # Save model and scaler
            self.models[symbol] = {
                'model': best_model,
                'type': model_type,
                'accuracy': max(rf_accuracy, gb_accuracy),
                'features': self.feature_columns
            }
            self.scalers[symbol] = scaler
            
            # Save to disk
            model_file = os.path.join(self.model_path, f"{symbol}_model.joblib")
            scaler_file = os.path.join(self.model_path, f"{symbol}_scaler.joblib")
            
            joblib.dump(best_model, model_file)
            joblib.dump(scaler, scaler_file)
            
            logger.info(f"✅ Model trained for {symbol} with {model_type} (Accuracy: {max(rf_accuracy, gb_accuracy):.3f})")
            return True
            
        except Exception as e:
            logger.error(f"Error training model for {symbol}: {e}")
            return False
            
    def load_model(self, symbol: str) -> bool:
        """Load trained model from disk"""
        try:
            model_file = os.path.join(self.model_path, f"{symbol}_model.joblib")
            scaler_file = os.path.join(self.model_path, f"{symbol}_scaler.joblib")
            
            if os.path.exists(model_file) and os.path.exists(scaler_file):
                model = joblib.load(model_file)
                scaler = joblib.load(scaler_file)
                
                self.models[symbol] = {
                    'model': model,
                    'type': type(model).__name__,
                    'accuracy': 0.0,  # Could be loaded from metadata
                    'features': self.feature_columns
                }
                self.scalers[symbol] = scaler
                
                logger.info(f"✅ Model loaded for {symbol}")
                return True
            else:
                logger.warning(f"No saved model found for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading model for {symbol}: {e}")
            return False
            
    def predict_signal(self, symbol: str, data: pd.DataFrame, indicators: Dict) -> Dict[str, any]:
        """Predict trading signal using ML model"""
        try:
            if symbol not in self.models:
                if not self.load_model(symbol):
                    # Train new model if none exists
                    if not self.train_model(symbol, data, indicators):
                        return {'prediction': 0, 'confidence': 0, 'probabilities': []}
                        
            model_info = self.models[symbol]
            scaler = self.scalers[symbol]
            
            # Prepare features
            features = self.prepare_features(data, indicators)
            
            if features.empty:
                return {'prediction': 0, 'confidence': 0, 'probabilities': []}
                
            # Get latest features
            latest_features = features.iloc[-1:][model_info['features']]
            
            # Scale features
            latest_features_scaled = scaler.transform(latest_features)
            
            # Make prediction
            prediction = model_info['model'].predict(latest_features_scaled)[0]
            probabilities = model_info['model'].predict_proba(latest_features_scaled)[0]
            
            # Calculate confidence as max probability
            confidence = max(probabilities) * 100
            
            return {
                'prediction': int(prediction),
                'confidence': confidence,
                'probabilities': probabilities.tolist(),
                'model_type': model_info['type'],
                'model_accuracy': model_info['accuracy']
            }
            
        except Exception as e:
            logger.error(f"Error predicting signal for {symbol}: {e}")
            return {'prediction': 0, 'confidence': 0, 'probabilities': []}
            
    def get_feature_importance(self, symbol: str) -> Dict[str, float]:
        """Get feature importance for a model"""
        try:
            if symbol not in self.models:
                return {}
                
            model = self.models[symbol]['model']
            features = self.models[symbol]['features']
            
            if hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
                return dict(zip(features, importance))
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting feature importance for {symbol}: {e}")
            return {}
            
    def retrain_all_models(self, market_data: Dict) -> bool:
        """Retrain all models with new data"""
        try:
            success_count = 0
            total_count = 0
            
            for symbol, data_info in market_data.items():
                total_count += 1
                if self.train_model(symbol, data_info['data'], data_info['indicators']):
                    success_count += 1
                    
            logger.info(f"Retrained {success_count}/{total_count} models successfully")
            return success_count == total_count
            
        except Exception as e:
            logger.error(f"Error retraining models: {e}")
            return False
            
    def ensemble_prediction(self, predictions: List[Dict]) -> Dict[str, any]:
        """Combine multiple ML predictions using ensemble method"""
        try:
            if not predictions:
                return {'prediction': 0, 'confidence': 0}
                
            # Weight predictions by model accuracy
            weighted_sum = 0
            total_weight = 0
            confidence_sum = 0
            
            for pred in predictions:
                weight = pred.get('model_accuracy', 0.5)
                weighted_sum += pred['prediction'] * weight
                total_weight += weight
                confidence_sum += pred['confidence'] * weight
                
            if total_weight == 0:
                return {'prediction': 0, 'confidence': 0}
                
            ensemble_prediction = weighted_sum / total_weight
            ensemble_confidence = confidence_sum / total_weight
            
            # Convert to discrete signal
            if ensemble_prediction > 0.3:
                signal = 1  # Buy
            elif ensemble_prediction < -0.3:
                signal = -1  # Sell
            else:
                signal = 0  # Hold
                
            return {
                'prediction': signal,
                'confidence': ensemble_confidence,
                'raw_prediction': ensemble_prediction
            }
            
        except Exception as e:
            logger.error(f"Error in ensemble prediction: {e}")
            return {'prediction': 0, 'confidence': 0}
