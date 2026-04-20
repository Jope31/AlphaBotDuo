# **🤖 AlphaBot: Intelligent Profit and Loss Guardian (v2.0 "Risk Guard")**

AlphaBot is an advanced, automated risk-management and trailing-stop execution engine designed to interface directly with Composer.trade portfolios. By combining real-time intraday data from Alpaca with K-Nearest Neighbor Monte Carlo simulations, AlphaBot acts as an intelligent circuit breaker—defending your portfolio against sudden intraday breakdowns and locking in parabolic gains.

Recently upgraded with empirical data from live-market "Risk Guard" post-mortems, AlphaBot (v2.0) has evolved from a static script into a highly sophisticated, noise-resistant execution engine.

## **🌟 Key Upgrades & Core Features**

Theoretical safety nets often trigger on market microstructure noise. AlphaBot introduces several core features designed specifically to eliminate false positives and keep you in the trade:

1. **Volatility-Scaled Loss Arming (The "Flash Crash" Filter):** Assets no longer arm on a flat percentage drop. A -1.5% drop is an emergency for a Treasury Bond, but normal noise for a 3x Leveraged ETF. AlphaBot now arms the trailing stop based on the asset's specific baseline: ```max(LOSS_ARM_PCT, Daily_Volatility)```.  
2. **Dynamic Multi-Tick Noise Confirmation:** To prevent execution on momentary bid/ask spread noise or single-tick flashes, a symphony must breach its stop level. AlphaBot dynamically scales this confirmation requirement based on multi-day 1-minute historical volatility (e.g., 3 consecutive ticks required for highly volatile assets like TQQQ; 1 tick for stable assets like LQD).  
3. **Extended Morning Grace Period:** AlphaBot bypasses the unpredictable opening hour, starting its logic only after the morning auction volatility settles.  
4. **Multi-Day Intraday Volatility Analysis (NEW):** AlphaBot analyzes the past 5 trading days of 1-minute intraday data for your target holdings to establish a rolling "Noise Floor" and an "EOD Volatility Ratio," ensuring it adapts to current market regimes.  
5. **EOD Relief Valve (NEW):** The logarithmic "Strangler" algorithm excels at locking in gains, but markets get notoriously choppy at 3:30 PM due to MOC orders. If an asset is historically prone to end-of-day volatility, AlphaBot dynamically relaxes the stop "squeeze" by up to 15%, giving it breathing room to survive closing bell fake-outs.  
6. **Two-Stage Post-Mortem Diagnostics (NEW):** Generates daily ```post_mortem_YYYY-MM-DD.json``` files for AI ingestion. Stage 1 (```15:54 ET```) locks in the math to calculate "Guard Alpha," and Stage 2 (```16:00 ET```) runs next-day volatility prep on tomorrow's target holdings.

7. **Gemini "Quant Analyst" Integration (NEW)**

The ```post_mortem_YYYY-MM-DD.json``` file is specifically structured to be analyzed by a Large Language Model (like Google Gemini Gems).

**How to set up your AI Analyst:**

1. Create a new custom Persona/Gem in Gemini.  
2. Name it "AlphaBot Quant Analyst".  
3. Paste the following into the system instructions:
```
You are a Quantitative Risk Analyst evaluating the daily performance of "AlphaBot," an intraday trailing stop-loss execution system.

Every day, I will provide you with:

1. The daily "post_mortem_YYYY-MM-DD.json" file.  
2. The closing context of the market (e.g., "SPY +1.2%, QQQ \+0.8%, head-fake morning recovery").

Your job is to generate a structured post-mortem report mirroring standard quant desk formatting.

Required Instructions:

1. **Market Context:** Briefly summarize the trading day regime based on my input.  
2. **Activity Summary:** State how many symphonies were monitored vs. triggered.  
3. **Guard Alpha Analysis:** Calculate the overall Win Rate (what percentage of triggers had a positive ```saved_pct_guard_alpha```). Calculate the median and average ```saved_pct_guard_alpha```.  
4. **Trigger Breakdown:** Differentiate between "Take-Profit" triggers and "Trailing Stop" triggers. Note which one performed better.  
5. **Noise & Microstructure Analysis:** Look at the time_triggered values. Did a large cluster trigger at the same time? Look at triggers with a saved_pct_guard_alpha between -0.10% and 0.0%. Call these out as potential "Noise Crossings."  
6. **Forward-Looking Recommendations:** Review the "tomorrow_target_holdings" object in the JSON file.  
   * Identify the dominant asset classes carrying over into tomorrow.  
   * If the portfolio is rotating into highly volatile/leveraged assets (like TQQQ or SOXL), assess if LOSS_ARM_PCT needs to be raised to account for larger intraday swings.  
   * If the portfolio is rotating into safe/low-volatility assets, assess if ```TRIGGER_THRESHOLD_PCT``` should be tightened.  
   * Provide 1 or 2 specific strategy parameter adjustments for the next trading session.
```
**Daily Workflow:** Simply drop the generated JSON file into the chat at 4:05 PM ET and provide a 1-sentence market summary. The AI will provide a complete statistical breakdown and parameter tuning advice for tomorrow.


## **⚙️ Environment Variables**

* ```LIVE_EXECUTION``` *(Default: False)* - Master safety switch. When False, AlphaBot operates in a Dry Run mode, logging logic and sending Discord alerts without executing API trades.  
* ```TRIGGER_THRESHOLD_PCT``` *(Default: 15.0)* - The Monte Carlo probability required to "arm" the trailing stop logic.  
* ```TAKE_PROFIT_MC_PCT``` *(Default: 5.0)* - The extreme top-percentile Monte Carlo probability required to arm the Take-Profit trap.  
* ```MAX_SQUEEZE_FLOOR``` *(Default: 0.20)* - The maximum amount the "Strangler" can tighten a stop by 4:00 PM (e.g., tightens to 20% of its original distance).  
* ```LOSS_ARM_PCT``` *(Default: 1.5)* - The hard volatility floor percentage to arm the stop during a sudden breakdown.  
* ```BASE_ATR_MULTIPLIER``` *(Default: 2.0)* - The multiplier applied to the asset's 20-day volatility to calculate the initial morning stop distance.  
* ```TRAILING_STOP_PCT``` *(Default: 1.5)* - The fallback trailing stop percentage.  
* ```BREAKEVEN_ACTIVATION_PCT``` *(Default: 2.0)* - The profit percentage required to lock the trailing stop at ```0.0%```, scaled dynamically against daily volatility.

## **🚀 Setup & Installation**

1. **Clone the Repository:**  
```
   git clone https://github.com/Jope31/AlphaBot.git  
   cd AlphaBot
```

2. **Install Dependencies:**
```
   pip install flask python-dotenv requests numpy schedule pandas alpaca-trade-api
```

3. **Configure Environment:** Create a .env file in the root directory and populate it with the variables listed in the Environment section above (including your Composer, Alpaca, and Discord API keys).  

4. **Launch the Control Center:**
```
   python app.py
```
   *The Flask server will start on ```http://localhost:5000``` and automatically spawn the background execution scheduler.*

## 🕒 Scheduling Details

AlphaBot utilizes a background schedule thread running via ```app.py```.

* 1-Minute Ticks: The bot evaluates your portfolio precisely at the top of every minute (```:00```) to support the dynamic tick confirmation logic.    
* 10:30 AM Grace Period: The bot explicitly ignores the highly volatile market open and begins its daily execution loop at ```10:30 AM ET```.    
* Rebalance Blackout: Executions are automatically paused just before ```3:55 PM ET``` to prevent API collisions with Composer's daily rebalancing routines.

**Disclaimer: AlphaBot is an automated execution tool. Algorithmic trading carries significant risk. Always test parameters in Dry Run mode before enabling ```LIVE_EXECUTION```.**
