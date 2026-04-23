# **🤖 AlphaBot: Multi-Factor Volatility Engine (v4.0)**

AlphaBot is a high-performance quantitative risk-management framework and automated execution engine designed to interface directly with **Composer.trade** portfolios. By synthesizing real-time market sentiment (```VIX```), intraday time decay, structural volume support (True VWAP), and individual asset velocity, AlphaBot acts as an intelligent circuit breaker—protecting capital during systemic breakdowns while aggressively locking in gains during parabolic runs.

AlphaBot (v4.0) marks the transition from a static execution script to a **Self-Optimizing Risk Engine**. It features a High-Concurrency SQLite Backend for robust state management and a daily Walk-Forward Optimization engine that continuously adapts the bot's defensive parameters to shifting market regimes.

## **🌟 Core Defensive Architecture**

AlphaBot no longer uses a "one-size-fits-all" trailing stop. It layers multiple distinct mathematical forces to dynamically manage risk every minute of the trading day:

### **1. The Macro Foundation (VIX Regime Filter)**

The bot determines the "Market Weather" using the **VIX Index**. Instead of a static baseline, it sets your trailing stop multiplier dynamically based on current market fear:

* **Low Volatility (<15 ```VIX```):** Clamps stops tight (```VIX_LOW_MULT```) to prevent "slow bleed" losses in sideways chop.  
* **Normal Regime (15-25 ```VIX```):** Balanced sensitivity (```VIX_MID_MULT```) for standard market conditions.  
* **Crisis Regime (>25 ```VIX```):** Widens stops (```VIX_HIGH_MULT```) to allow for the systemic noise inherent in high-fear markets, preventing you from being shaken out by standard intraday volatility.

### **2. Monte Carlo Probabilistic Arming**

Instead of arbitrary entry points, AlphaBot uses a localized Monte Carlo engine. It compares a symphony’s intraday return against 5,000 simulated paths generated from 3 years of historical correlation and today’s live market momentum (```SPY``` proxy). When the probability of the symphony continuing to beat its simulated peers falls below ```TRIGGER_THRESHOLD_PCT```, the defensive trailing stop is "Armed."

### **3. Logarithmic Time-Decay Trailing Stop**

AlphaBot acknowledges that market volatility often increases toward the close. It calculates a trailing stop that tightens throughout the day based on a logarithmic decay curve:

* **Morning:** The stop is wider (starting at ```TRAILING_STOP_PCT```), allowing the primary trend to establish.  
* **Afternoon:** The stop aggressively "strangles" the price, narrowing toward ```ENDING_STOP_PCT``` to ensure that morning gains do not bleed out during End-of-Day profit-taking.

### **4. True VWAP (Volume Weighted Average Price) Defense**

This feature acts as a structural momentum backstop. The bot calculates the True VWAP for every individual holding within a symphony minute-by-minute. If a symphony achieves a High Water Mark (HWM) over ```VWAP_CROSS_HWM_PCT``` but its aggregate, allocation-weighted price falls below VWAP support for three consecutive minutes, the bot triggers an immediate exit, bypassing standard percentage drops to exit on fundamental momentum failure.

### **5. Asymmetric Parabolic Squeeze**

When a symphony undergoes a "vertical" run, the bot calculates its **Velocity Ratio** (HWM divided by rolling 20-day volatility). If this ratio exceeds the ```PARABOLIC_VELOCITY_THRESHOLD```, the bot applies an asymmetric squeeze, reducing the allowable drawdown percentage by up to ```MAX_PARABOLIC_SQUEEZE``` to tightly trap the peak.

### **6. Smart Take-Profit (TP)**

If a symphony experiences an exceptional gain that drops its Monte Carlo "beat probability" to extreme lows (below ```TAKE_PROFIT_MC_PCT```), a highly sensitive Take-Profit trap is armed. If momentum stalls, it exits immediately to capture the blow-off top.

## **🧠 The EOD Autotuner (Walk-Forward Optimization)**

At 4:00 PM ET, AlphaBot stops trading and transitions into an optimization engine.

1. **The Archive:** It saves the exact minute-by-minute price, volume, and probability data for every symphony into a permanent SQLite archive.  
2. **The Grid Search:** It pulls a rolling 5-day window of this data and replays it against **26,244** unique combinations of the bot's strategy variables.  
3. **Guard Alpha:** It scores every combination based on **Guard Alpha**—the exact percentage of capital that would have been saved by the bot's exits compared to passively holding to the close.  
4. **Self-Correction:** The bot finds the most mathematically optimal variable setup for the current market environment, **automatically overwrites the ```.env``` file**, and pushes a 2D Heatmap of the parameter space to Discord for visual review.

## **⚙️ Variable Glossary**

Configure these in your local dashboard or ```.env``` file. (Note: The Autotuner will optimize the primary Strategy variables nightly).

### **API & Core**

* ```LIVE_EXECUTION```: Boolean (True/False). Set to False to simulate trades safely.  
* ```COMPOSER_KEY_ID``` / ```COMPOSER_SECRET```: Composer API credentials.  
* ```ACCOUNT_UUIDS```: Comma-separated Composer account IDs.  
* ```ALPACA_KEY``` / ```ALPACA_SECRET```: Alpaca Market Data API credentials.  
* ```DISCORD_WEBHOOK_URL```: (Optional) URL for Live Alerts, EOD Snapshots, and Autotune Heatmaps.

### **Strategy & Defense**

* ```TRIGGER_THRESHOLD_PCT```: The MC probability threshold (e.g., 15.0%) that "Arms" the standard trailing stop.  
* ```TAKE_PROFIT_MC_PCT```: The extreme MC probability threshold (e.g., 5.0%) that arms the Smart TP.  
* ```LOSS_ARM_PCT```: A hard floor; if a symphony drops below this % (or its daily vol), it arms instantly.  
* ```BREAKEVEN_ACTIVATION_PCT```: The HWM % required to permanently lock the stop-loss above 0.0%.  
* ```MAX_SQUEEZE_FLOOR```: The maximum limit applied to the dynamic stop-loss during a high-conviction strangle.  
* ```VWAP_CROSS_HWM_PCT```: The minimum HWM required before the VWAP support breakdown defense is activated.  
* ```MIN_MULTIPLIER_FLOOR```: The absolute minimum distance the stop is allowed to sit from the current price.

### **Volatility Regimes & Parabolic Scaling**

* ```VIX_LOW_MULT```: The multiplier applied to volatility when ```VIX``` is < 15 (Default: 1.5).  
* ```VIX_MID_MULT```: The multiplier applied when ```VIX``` is 15-25 (Default: 2.0).  
* ```VIX_HIGH_MULT```: The multiplier applied when ```VIX``` is > 25 (Default: 2.5).  
* ```PARABOLIC_VELOCITY_THRESHOLD```: The ratio of HWM to Volatility that classifies a run as "parabolic."  
* ```MAX_PARABOLIC_SQUEEZE```: The maximum % reduction applied to the stop distance during a parabolic move.

### **Engine Fallbacks & Calculators**

* ```TRAILING_STOP_PCT```: Fallback starting stop percentage if historical volatility data is unavailable.  
* ```ENDING_STOP_PCT```: Fallback ending stop percentage if historical volatility data is unavailable.  
* ```SIMULATION_PATHS```: The number of paths generated for Monte Carlo analysis (Default: 5000).  
* ```NEIGHBOR_K```: The number of historical "nearest neighbor" days used to seed MC simulations (Default: 150).

## **🚀 Setup & Installation**

1. **Clone the Repository:**
```   
   git clone https://github.com/Jope31/AlphaBot.git
   cd AlphaBot
```

2. **Install Dependencies:**
```  
pip install flask python-dotenv requests numpy schedule pandas alpaca-trade-api matplotlib seaborn
```

3. **Configure Environment:** Create a ```.env``` file in the root directory and populate it with your API keys. The mathematical variables will be generated upon first launch.  

4. **Launch the Control Center:**
```
python app.py
```

5. **Access Dashboard**:  
   Open ```http://localhost:5000```. The bot will automatically initialize the SQLite database on its first run.

## **🕒 Scheduling Details**

AlphaBot utilizes a background schedule thread running via ```app.py```.

* **10:30 AM ET Grace Period:** AlphaBot ignores the chaotic opening auction, beginning evaluations once the "Morning Noise" settles.  
* **3:54 PM ET Rebalance Blackout:** To prevent API collisions during Composer's rebalancing window, AlphaBot automatically ceases all execution actions 6 minutes before the close.  
* **4:00 PM ET EOD Processing:** AlphaBot locks final Shadow Returns, computes Guard Alpha, pushes the daily post-mortem to Discord, and begins the Walk-Forward Autotuning Grid Search.

*Disclaimer: AlphaBot is an automated execution tool. Algorithmic trading carries significant risk. Always test parameters in Dry Run mode before enabling ```LIVE_EXECUTION```.*
