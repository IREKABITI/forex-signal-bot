/**
 * #IREKABITI_FX Mobile App JavaScript
 * AI-Powered Trading Ecosystem Frontend
 */

class IrekabiFXApp {
    constructor() {
        this.API_BASE = '/api';
        this.WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;
        this.authToken = localStorage.getItem('auth_token');
        this.currentTab = 'dashboard';
        this.websocket = null;
        this.notifications = [];
        this.cache = new Map();
        this.refreshIntervals = new Map();
        
        this.init();
    }

    async init() {
        try {
            // Show loading screen
            this.showLoadingScreen();
            
            // Initialize service worker for PWA
            await this.initServiceWorker();
            
            // Check authentication
            if (this.authToken) {
                const isValid = await this.validateToken();
                if (isValid) {
                    await this.initMainApp();
                } else {
                    this.showLoginScreen();
                }
            } else {
                this.showLoginScreen();
            }
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Initialize PWA install prompt
            this.initPWAPrompt();
            
        } catch (error) {
            console.error('App initialization failed:', error);
            this.showToast('Failed to initialize app', 'error');
        }
    }

    async initServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                await navigator.serviceWorker.register('/sw.js');
                console.log('Service Worker registered successfully');
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        }
    }

    showLoadingScreen() {
        document.getElementById('loading-screen').classList.remove('hidden');
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('main-app').classList.add('hidden');
    }

    showLoginScreen() {
        document.getElementById('loading-screen').classList.add('hidden');
        document.getElementById('login-screen').classList.remove('hidden');
        document.getElementById('main-app').classList.add('hidden');
    }

    async showMainApp() {
        document.getElementById('loading-screen').classList.add('hidden');
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('main-app').classList.remove('hidden');
        
        // Load initial data
        await this.loadDashboardData();
        
        // Connect WebSocket
        this.connectWebSocket();
        
        // Start refresh intervals
        this.startRefreshIntervals();
    }

    setupEventListeners() {
        // Login form
        document.getElementById('login-form').addEventListener('submit', this.handleLogin.bind(this));
        
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.switchTab(tab);
            });
        });
        
        // Settings
        document.getElementById('min-confidence').addEventListener('input', (e) => {
            document.getElementById('min-confidence-value').textContent = e.target.value + '%';
        });
        
        // Modal close
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal();
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    async handleLogin(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const loginBtn = document.querySelector('.login-btn');
        const btnText = loginBtn.querySelector('.btn-text');
        const btnSpinner = loginBtn.querySelector('.btn-spinner');
        
        try {
            // Show loading state
            btnText.classList.add('hidden');
            btnSpinner.classList.remove('hidden');
            loginBtn.disabled = true;
            
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.authToken = data.access_token;
                localStorage.setItem('auth_token', this.authToken);
                
                await this.initMainApp();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Login failed');
            }
            
        } catch (error) {
            console.error('Login error:', error);
            this.showError('Connection failed. Please try again.');
        } finally {
            // Reset button state
            btnText.classList.remove('hidden');
            btnSpinner.classList.add('hidden');
            loginBtn.disabled = false;
        }
    }

    async validateToken() {
        try {
            const response = await this.apiCall('/dashboard/summary');
            return response.success;
        } catch {
            return false;
        }
    }

    async initMainApp() {
        await this.showMainApp();
        this.showToast('Welcome to #IREKABITI_FX!', 'success');
    }

    switchTab(tabName) {
        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update content
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        this.currentTab = tabName;
        
        // Load tab-specific data
        this.loadTabData(tabName);
    }

    async loadTabData(tabName) {
        switch (tabName) {
            case 'dashboard':
                await this.loadDashboardData();
                break;
            case 'signals':
                await this.loadSignalsData();
                break;
            case 'portfolio':
                await this.loadPortfolioData();
                break;
            case 'analytics':
                await this.loadAnalyticsData();
                break;
            case 'settings':
                this.loadSettingsData();
                break;
        }
    }

    async loadDashboardData() {
        try {
            const data = await this.apiCall('/dashboard/summary');
            
            if (data.success) {
                this.updateDashboardStats(data.data);
                this.updateLatestSignals(data.data.recent_signals);
                this.updateMarketOverview(data.data);
            }
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showToast('Failed to load dashboard data', 'error');
        }
    }

    updateDashboardStats(data) {
        document.getElementById('total-signals').textContent = data.performance?.total_signals || '-';
        document.getElementById('win-rate').textContent = data.performance?.win_rate ? `${data.performance.win_rate.toFixed(1)}%` : '-';
        document.getElementById('total-pnl').textContent = data.performance?.total_return ? `${data.performance.total_return.toFixed(2)}%` : '-';
        document.getElementById('avg-confidence').textContent = data.performance?.avg_confidence ? `${data.performance.avg_confidence.toFixed(0)}` : '-';
        
        // Update market status
        const marketStatus = document.getElementById('market-status');
        const isForexOpen = data.market_status?.forex;
        marketStatus.textContent = isForexOpen ? '🟢 Markets Open' : '🔴 Markets Closed';
        
        // Update active session
        document.getElementById('active-session').textContent = data.active_session || 'Closed';
        if (data.active_session && data.active_session !== 'Closed') {
            document.getElementById('active-session').className = 'session-badge active';
        }
    }

    updateLatestSignals(signals) {
        const container = document.getElementById('latest-signals');
        
        if (!signals || signals.length === 0) {
            container.innerHTML = '<div class="no-data">No recent signals</div>';
            return;
        }
        
        container.innerHTML = signals.slice(0, 3).map(signal => `
            <div class="signal-card" onclick="app.showSignalDetails('${signal.symbol}')">
                <div class="signal-header">
                    <span class="signal-symbol">${signal.symbol}</span>
                    <span class="signal-direction ${signal.direction.toLowerCase()}">${signal.direction}</span>
                </div>
                <div class="signal-details">
                    <div class="signal-detail">
                        <div class="signal-detail-label">Entry</div>
                        <div class="signal-detail-value">${signal.entry_price}</div>
                    </div>
                    <div class="signal-detail">
                        <div class="signal-detail-label">Confidence</div>
                        <div class="signal-detail-value">${signal.confidence}%</div>
                    </div>
                </div>
                <div class="signal-confidence">
                    <span>Risk: ${signal.risk_percent}%</span>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${signal.confidence}%"></div>
                    </div>
                    <span>${signal.timeframe}</span>
                </div>
            </div>
        `).join('');
    }

    updateMarketOverview(data) {
        const container = document.getElementById('market-overview');
        
        const majorPairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSDT', 'ETHUSDT'];
        
        container.innerHTML = `
            <div class="market-grid">
                ${majorPairs.map(pair => `
                    <div class="market-item">
                        <div class="market-symbol">${pair}</div>
                        <div class="market-price">Loading...</div>
                        <div class="market-change">-</div>
                    </div>
                `).join('')}
            </div>
        `;
        
        // Load current prices
        this.loadMarketPrices(majorPairs);
    }

    async loadMarketPrices(symbols) {
        try {
            const response = await this.apiCall(`/market/prices?symbols=${symbols.join(',')}`);
            
            if (response.success) {
                symbols.forEach(symbol => {
                    const price = response.data[symbol];
                    if (price) {
                        const priceElement = document.querySelector(`[data-symbol="${symbol}"] .market-price`);
                        if (priceElement) {
                            priceElement.textContent = price.toFixed(5);
                        }
                    }
                });
            }
        } catch (error) {
            console.error('Failed to load market prices:', error);
        }
    }

    async loadSignalsData() {
        try {
            const data = await this.apiCall('/signals/latest?limit=20');
            
            if (data.success) {
                this.updateSignalsList(data.data);
            }
        } catch (error) {
            console.error('Failed to load signals data:', error);
            this.showToast('Failed to load signals', 'error');
        }
    }

    updateSignalsList(signals) {
        const container = document.getElementById('signals-list');
        
        if (!signals || signals.length === 0) {
            container.innerHTML = '<div class="no-data">No signals available</div>';
            return;
        }
        
        container.innerHTML = signals.map(signal => `
            <div class="signal-card" onclick="app.showSignalDetails('${signal.symbol}')">
                <div class="signal-header">
                    <div>
                        <div class="signal-symbol">${signal.symbol}</div>
                        <div class="signal-time">${this.formatTime(signal.timestamp)}</div>
                    </div>
                    <span class="signal-direction ${signal.direction.toLowerCase()}">${signal.direction}</span>
                </div>
                <div class="signal-details">
                    <div class="signal-detail">
                        <div class="signal-detail-label">Entry</div>
                        <div class="signal-detail-value">${signal.entry_price}</div>
                    </div>
                    <div class="signal-detail">
                        <div class="signal-detail-label">TP</div>
                        <div class="signal-detail-value">${signal.tp_price}</div>
                    </div>
                    <div class="signal-detail">
                        <div class="signal-detail-label">SL</div>
                        <div class="signal-detail-value">${signal.sl_price}</div>
                    </div>
                    <div class="signal-detail">
                        <div class="signal-detail-label">Risk</div>
                        <div class="signal-detail-value">${signal.risk_percent}%</div>
                    </div>
                </div>
                <div class="signal-confidence">
                    <span>Confidence: ${signal.confidence}%</span>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${signal.confidence}%"></div>
                    </div>
                    <span>${signal.timeframe}</span>
                </div>
                <div class="signal-analysis">${signal.analysis}</div>
            </div>
        `).join('');
    }

    async loadPortfolioData() {
        try {
            const data = await this.apiCall('/portfolio/optimize');
            
            if (data.success && data.data.success) {
                this.updatePortfolioMetrics(data.data);
                this.updatePortfolioAllocation(data.data.weights);
            } else {
                this.showToast('Portfolio optimization not available', 'warning');
            }
        } catch (error) {
            console.error('Failed to load portfolio data:', error);
            this.showToast('Failed to load portfolio data', 'error');
        }
    }

    updatePortfolioMetrics(data) {
        document.getElementById('expected-return').textContent = `${data.expected_return?.toFixed(2)}%`;
        document.getElementById('volatility').textContent = `${data.volatility?.toFixed(2)}%`;
        document.getElementById('sharpe-ratio').textContent = data.sharpe_ratio?.toFixed(2);
        document.getElementById('risk-score').textContent = `${data.risk_score}/100`;
    }

    updatePortfolioAllocation(weights) {
        const container = document.getElementById('portfolio-allocation');
        
        if (!weights || Object.keys(weights).length === 0) {
            container.innerHTML = '<div class="no-data">No allocation data available</div>';
            return;
        }
        
        const allocationHtml = Object.entries(weights)
            .sort(([,a], [,b]) => b - a)
            .map(([symbol, weight]) => `
                <div class="allocation-item">
                    <span class="allocation-symbol">${symbol}</span>
                    <span class="allocation-weight">${(weight * 100).toFixed(1)}%</span>
                    <div class="allocation-bar">
                        <div class="allocation-fill" style="width: ${weight * 100}%"></div>
                    </div>
                </div>
            `).join('');
        
        container.innerHTML = allocationHtml;
    }

    async loadAnalyticsData() {
        try {
            const period = document.getElementById('analytics-period').value;
            const data = await this.apiCall(`/analytics/performance?days=${period}`);
            
            if (data.success) {
                this.updatePerformanceChart(data.data);
                this.updateTopPerformers(data.data.trading_stats);
                this.updateNewsImpact();
            }
        } catch (error) {
            console.error('Failed to load analytics data:', error);
            this.showToast('Failed to load analytics', 'error');
        }
    }

    updatePerformanceChart(data) {
        const container = document.getElementById('performance-chart');
        
        // Simple text-based performance display
        const stats = data.trading_stats;
        container.innerHTML = `
            <div class="performance-summary">
                <div class="perf-metric">
                    <span class="perf-label">Total Signals:</span>
                    <span class="perf-value">${stats.total_signals}</span>
                </div>
                <div class="perf-metric">
                    <span class="perf-label">Win Rate:</span>
                    <span class="perf-value">${stats.win_rate?.toFixed(1)}%</span>
                </div>
                <div class="perf-metric">
                    <span class="perf-label">Total Return:</span>
                    <span class="perf-value">${stats.total_return?.toFixed(2)}%</span>
                </div>
                <div class="perf-metric">
                    <span class="perf-label">Sharpe Ratio:</span>
                    <span class="perf-value">${stats.sharpe_ratio?.toFixed(2)}</span>
                </div>
            </div>
        `;
    }

    updateTopPerformers(stats) {
        const container = document.getElementById('top-performers');
        
        if (!stats.top_pairs || Object.keys(stats.top_pairs).length === 0) {
            container.innerHTML = '<div class="no-data">No performance data available</div>';
            return;
        }
        
        const performersHtml = Object.entries(stats.top_pairs)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5)
            .map(([symbol, performance]) => `
                <div class="performer-item">
                    <span class="performer-symbol">${symbol}</span>
                    <span class="performer-return ${performance >= 0 ? 'positive' : 'negative'}">
                        ${performance >= 0 ? '+' : ''}${performance.toFixed(1)}%
                    </span>
                </div>
            `).join('');
        
        container.innerHTML = performersHtml;
    }

    async updateNewsImpact() {
        try {
            const data = await this.apiCall('/news/summary');
            
            if (data.success && data.data.articles) {
                const container = document.getElementById('news-impact');
                
                const newsHtml = data.data.articles.slice(0, 3).map(article => `
                    <div class="news-item">
                        <div class="news-title">${article.title}</div>
                        <div class="news-source">${article.source}</div>
                        <div class="news-time">${this.formatTime(article.published_at)}</div>
                    </div>
                `).join('');
                
                container.innerHTML = newsHtml;
            }
        } catch (error) {
            console.error('Failed to load news data:', error);
        }
    }

    loadSettingsData() {
        // Load settings from localStorage or defaults
        const settings = this.getSettings();
        
        document.getElementById('push-notifications').checked = settings.pushNotifications;
        document.getElementById('email-notifications').checked = settings.emailNotifications;
        document.getElementById('min-confidence').value = settings.minConfidence;
        document.getElementById('min-confidence-value').textContent = `${settings.minConfidence}%`;
        document.getElementById('theme-select').value = settings.theme;
        document.getElementById('currency-select').value = settings.currency;
    }

    getSettings() {
        const defaults = {
            pushNotifications: true,
            emailNotifications: false,
            minConfidence: 70,
            theme: 'dark',
            currency: 'USD'
        };
        
        const stored = localStorage.getItem('app_settings');
        return stored ? { ...defaults, ...JSON.parse(stored) } : defaults;
    }

    saveSettings() {
        const settings = {
            pushNotifications: document.getElementById('push-notifications').checked,
            emailNotifications: document.getElementById('email-notifications').checked,
            minConfidence: parseInt(document.getElementById('min-confidence').value),
            theme: document.getElementById('theme-select').value,
            currency: document.getElementById('currency-select').value
        };
        
        localStorage.setItem('app_settings', JSON.stringify(settings));
        this.showToast('Settings saved', 'success');
    }

    async scanMarkets() {
        try {
            this.showToast('Scanning markets...', 'info');
            
            const data = await this.apiCall('/market/scan');
            
            if (data.success) {
                const results = data.data;
                this.showToast(
                    `Scan complete: ${results.high_confidence} high-confidence opportunities found`,
                    'success'
                );
                
                // Refresh signals data
                if (this.currentTab === 'signals') {
                    await this.loadSignalsData();
                }
            }
        } catch (error) {
            console.error('Market scan failed:', error);
            this.showToast('Market scan failed', 'error');
        }
    }

    async optimizePortfolio() {
        try {
            this.showToast('Optimizing portfolio...', 'info');
            
            const data = await this.apiCall('/portfolio/optimize');
            
            if (data.success && data.data.success) {
                this.showToast('Portfolio optimized successfully', 'success');
                await this.loadPortfolioData();
            } else {
                this.showToast('Portfolio optimization failed', 'error');
            }
        } catch (error) {
            console.error('Portfolio optimization failed:', error);
            this.showToast('Optimization failed', 'error');
        }
    }

    async refreshSignals() {
        await this.loadSignalsData();
        this.showToast('Signals refreshed', 'success');
    }

    filterSignals() {
        const filter = document.getElementById('signal-filter').value;
        // Implement signal filtering logic
        console.log('Filtering signals by:', filter);
    }

    updateAnalytics() {
        this.loadAnalyticsData();
    }

    showSignalDetails(symbol) {
        // Implementation for showing detailed signal information
        document.getElementById('modal-title').textContent = `${symbol} Signal Details`;
        document.getElementById('signal-details').innerHTML = `
            <div class="signal-detail-content">
                <h4>Technical Analysis</h4>
                <p>Detailed technical analysis for ${symbol}...</p>
                
                <h4>Risk Management</h4>
                <p>Risk assessment and position sizing recommendations...</p>
                
                <h4>Market Context</h4>
                <p>Current market conditions and sentiment...</p>
            </div>
        `;
        
        document.getElementById('signal-modal').classList.remove('hidden');
    }

    closeModal() {
        document.getElementById('signal-modal').classList.add('hidden');
    }

    connectWebSocket() {
        try {
            this.websocket = new WebSocket(this.WS_URL);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                document.getElementById('connection-status').textContent = '🟢 Connected';
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                document.getElementById('connection-status').textContent = '🔴 Disconnected';
                
                // Attempt to reconnect after 5 seconds
                setTimeout(() => this.connectWebSocket(), 5000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'new_signal':
                this.showToast(`New signal: ${data.data.symbol} ${data.data.direction}`, 'success');
                if (this.currentTab === 'signals' || this.currentTab === 'dashboard') {
                    this.loadTabData(this.currentTab);
                }
                break;
            case 'signal_update':
                // Handle signal updates
                break;
            case 'market_update':
                // Handle market updates
                break;
        }
    }

    startRefreshIntervals() {
        // Refresh dashboard every 30 seconds
        this.refreshIntervals.set('dashboard', setInterval(() => {
            if (this.currentTab === 'dashboard') {
                this.loadDashboardData();
            }
        }, 30000));
        
        // Refresh signals every 60 seconds
        this.refreshIntervals.set('signals', setInterval(() => {
            if (this.currentTab === 'signals') {
                this.loadSignalsData();
            }
        }, 60000));
    }

    stopRefreshIntervals() {
        this.refreshIntervals.forEach((interval) => {
            clearInterval(interval);
        });
        this.refreshIntervals.clear();
    }

    async apiCall(endpoint, options = {}) {
        const url = `${this.API_BASE}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.authToken}`
            }
        };
        
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (response.status === 401) {
            this.logout();
            throw new Error('Unauthorized');
        }
        
        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }
        
        return await response.json();
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        document.getElementById('toast-container').appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    showError(message) {
        document.getElementById('login-error').textContent = message;
        document.getElementById('login-error').classList.remove('hidden');
        
        setTimeout(() => {
            document.getElementById('login-error').classList.add('hidden');
        }, 5000);
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
    }

    exportData() {
        // Implementation for data export
        this.showToast('Exporting data...', 'info');
    }

    logout() {
        localStorage.removeItem('auth_token');
        this.authToken = null;
        
        // Stop all intervals and close WebSocket
        this.stopRefreshIntervals();
        if (this.websocket) {
            this.websocket.close();
        }
        
        this.showLoginScreen();
        this.showToast('Logged out successfully', 'info');
    }

    // PWA Installation
    initPWAPrompt() {
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            
            // Show install prompt
            document.getElementById('install-prompt').classList.remove('hidden');
        });
        
        window.installApp = async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                
                if (outcome === 'accepted') {
                    this.showToast('App installed successfully!', 'success');
                }
                
                deferredPrompt = null;
                document.getElementById('install-prompt').classList.add('hidden');
            }
        };
        
        window.dismissInstall = () => {
            document.getElementById('install-prompt').classList.add('hidden');
        };
    }
}

// Global functions for HTML onclick events
window.refreshSignals = () => app.refreshSignals();
window.scanMarkets = () => app.scanMarkets();
window.optimizePortfolio = () => app.optimizePortfolio();
window.filterSignals = () => app.filterSignals();
window.updateAnalytics = () => app.updateAnalytics();
window.closeModal = () => app.closeModal();
window.exportData = () => app.exportData();
window.logout = () => app.logout();

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new IrekabiFXApp();
});

// Service Worker registration for PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
