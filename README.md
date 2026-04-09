# **Alpha Bot Control Center**

Alpha Bot is an automated trading and risk management system built for Composer.trade. It uses a **Hybrid MC-Armed Fixed Trailing Stop** to protect profits and enforce risk-free trades without overcomplicating execution logic.

The system features a live web dashboard that allows you to monitor the state of your portfolio across multiple accounts and dynamically adjust your API credentials and algorithmic risk parameters on the fly.

## **🌟 Key Features**

* **Live Web Dashboard:** Monitor all symphonies across your Composer accounts (Individual, Roth IRA, Trad. IRA) in real-time.  
* **Monte Carlo "Arming":** Simulates 5,000 potential future paths based on historical Alpaca data. If the probability of beating the current return drops below a threshold, the bot "arms" the trailing stop.  
* **Hybrid Trailing Stop:** Once armed, the bot follows the symphony's peak with a strict, predictable fixed percentage trailing stop, abandoning complex volatility math.  
* **Breakeven Lock:** The moment your symphony achieves a specific "Activation %" run, the bot violently yanks the stop level up to 0.00%, mathematically forbidding the trade from closing in the red.  
* **Post-Market Simulator:** Re-run the day's data with different trailing stops and breakeven locks to see exactly what would have triggered, allowing for perfect tuning.

## **📂 Project Structure**

Alpha\_Bot\_Project/  
├── .env&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; \# API Keys and Algorithm Parameters  
├── alpha\_bot\_execution.py&emsp;\# Core Bot Engine (Math, API Calls, Execution)  
├── app.py&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;\# Flask Web Server & Background Scheduler  
├── bot\_state.json&emsp;&emsp;&emsp;\# Local memory (High Water Marks, Armed status)  
└── templates/  
&emsp;&emsp;└── index.html&emsp;&emsp;&emsp;\# Web Dashboard UI

## **🚀 Installation & Setup**

1. **Install Python Dependencies:**  
   Ensure you have Python installed, then open your terminal and run:  
   ```pip install flask schedule python-dotenv requests numpy```

2. **Initial Configuration:**  
   Create an empty ```.env``` file in your root folder (or use your existing one). You can input all your keys directly through the web dashboard once it's running.  

3. **Run the Control Center:**  
   Start the master application:  
   ```python app.py```

4. **Access the Dashboard:**  
   Open your browser and navigate to ```http://localhost:5000```. Click **Edit Variables** to configure your accounts, keys, and risk settings.

## **🔌 Connection Status Indicators**

At the top right of your dashboard, you will see a live connection indicator next to the "Force Run Now" button:

* **🟢 System Online (Green Pulse):** Your web browser is successfully communicating with your local Python backend (```app.py```). Your dashboard is actively receiving live data updates every 5 seconds.  
* **🔴 Disconnected (Red Solid):** Your browser has lost connection to the backend. This almost always means the terminal window running ```app.py``` was closed, stopped, or crashed. The dashboard is now frozen. To fix this, simply restart python app.py in your terminal and the dashboard will reconnect automatically.

## **⏱️ Scheduling & Manual Triggers**

**Automated 24/7 Execution**

Once you start ```app.py```, it automatically runs **every 5 minutes**. It includes a **Market Hours Gatekeeper** that puts the bot to sleep at night and on weekends (outside 9:30 AM \- 4:00 PM ET) to save API calls.

**"Force Run Now" Mechanism**

Clicking the "Force Run Now" button on the dashboard immediately bypasses the timer *and* the Gatekeeper. It executes a live run instantly without interrupting the primary background schedule.

## **🎛️ Strategy Variables**

| Variable | Default | Description & Tuning |
| :---- | :---- | :---- |
| TRIGGER\_THRESHOLD\_PCT | 15.0 | **The "Arming" switch.** The % of Monte Carlo paths needed to beat the current return. *Lower (5.0)* \= Aggressive/Patient. *Higher (25.0)* \= Conservative/Nervous. |
| TRAILING\_STOP\_PCT | 1.5 | **The Leash.** Once the symphony is armed, the bot will trail the High Water Mark by this exact percentage. |
| BREAKEVEN\_ACTIVATION\_PCT | 2.0 | **The Lock.** When the High Water Mark hits this exact percentage, the bot forces the Stop Level to 0.00%, guaranteeing a risk-free trade. |

## **🛠️ How It Works (The Execution Loop)**

1. **Scheduler:** ```app.py``` triggers alpha\_bot\_execution.py every 5 minutes during market hours.  
2. **Data Fetching:** Retrieves returns from Composer and historical price data from Alpaca.  
3. **Evaluation:** Updates the local ```bot_state.json``` with the High Water Mark.  
4. **Monte Carlo:** Calculates the probability of beating the current return by end-of-day. If below ```TRIGGER_THRESHOLD_PCT```, the symphony is marked "armed": true.  
5. **Execution:** If Armed, the bot calculates the Stop Level (HWM \- Trailing Stop). It applies the Breakeven lock if necessary. If the Current Return drops below this Stop Level, it executes a sell-all command via the Composer API and sends a Discord alert.
