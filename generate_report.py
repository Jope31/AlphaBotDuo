import os
import json
from datetime import datetime, timedelta, timezone
from jinja2 import Environment, FileSystemLoader

def generate_daily_report():
    print("Generating End-of-Day HTML Report...")
    
    # Updated to use timezone-aware UTC
    today = (datetime.now(timezone.utc) - timedelta(hours=5)).strftime('%Y-%m-%d')
    
    log_file = f"reports/ledger_{today}.json"
    output_file = f"reports/report_{today}.html"

    # Ensure the reports folder exists
    if not os.path.exists("reports"):
        print("No reports folder found. Run alpha_bot.py first to log events.")
        return

    # Load today's events from the ledger
    events = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            try:
                events = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Log file {log_file} is corrupted or empty.")
    else:
        print(f"No event ledger found for {today}. A blank report will be generated.")

    # Organize events by account ID
    events_by_account = {}
    for event in events:
        # Graceful fallback to "Unknown Account" for older ledger entries
        acc = event.get('account', 'Unknown Account')
        if acc not in events_by_account:
            events_by_account[acc] = []
        events_by_account[acc].append(event)

    # Setup Jinja2 Environment
    env = Environment(loader=FileSystemLoader('.'))
    
    try:
        template = env.get_template('report_template.html')
    except Exception as e:
        print(f"Error loading template: {e}. Make sure report_template.html is in this folder.")
        return

    # Render the HTML using the grouped data
    has_events = len(events) > 0
    html_output = template.render(date=today, events_by_account=events_by_account, has_events=has_events)

    # Save the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)
        
    print(f"✅ Success! Report saved to: {output_file}")

if __name__ == "__main__":
    generate_daily_report()