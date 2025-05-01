import requests
import csv
import io
import os
from datetime import datetime, timedelta, timezone

def get_exchange_rate_from_sheet(from_currency, to_currency="THB"):
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS2aftALcPNDtrhi5sIER6WlZurs5SnEcQgATGGKj2I-NwlekzBdzm7HHNF189Wgt_rz85-OYLzXds9/pub?gid=0&single=true&output=csv"
    response = requests.get(csv_url)
    if response.status_code != 200:
        print("Error fetching Google Sheet.")
        return None

    f = io.StringIO(response.text)
    reader = csv.DictReader(f)
    for row in reader:
        if row['From'].strip().upper() == from_currency.strip().upper() and row['To'].strip().upper() == to_currency.strip().upper():
            try:
                return float(row['Rate'])
            except:
                return None
    return None

def print_receipt(customer_name, currency_data):
    total_thb = 0
    # Set timezone to GMT+7 (Bangkok)
    bangkok_tz = timezone(timedelta(hours=7))
    now = datetime.now(bangkok_tz)
    date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    receipt = (
        "="*40 + "\n"
        "        Currency Exchange Receipt\n"
        + "="*40 + "\n"
        f"Date & Time   : {date_time_str}\n"
        f"Customer Name : {customer_name}\n"
        + "-"*40 + "\n"
        f"{'Currency':<10}{'Amount':>10}{'Rate':>10}{'THB':>10}\n"
        + "-"*40 + "\n"
    )
    for currency, amount, rate in currency_data:
        thb_amount = amount * rate
        total_thb += thb_amount
        receipt += f"{currency:<10}{amount:>10.2f}{rate:>10.2f}{thb_amount:>10.2f}\n"
    receipt += (
        "-"*40 + "\n"
        f"{'Total (THB)':>30}{total_thb:>10.2f}\n"
        + "="*40 + "\n"
        "   Thank you for exchanging with us!\n"
        + "="*40 + "\n"
    )
    print(receipt)
    with open("receipt.txt", "w", encoding="utf-8") as f:
        f.write(receipt)
    # Automatically print the receipt (Windows only)
    try:
        os.startfile("receipt.txt", "print")
    except Exception as e:
        print("Auto-print failed:", e)

# Interactive input
default_customer = "Customer"
customer = input(f"Enter customer name (default: {default_customer}): ").strip()
if not customer:
    customer = default_customer

currency_data = []

while True:
    currency = input("Enter source currency (e.g., USD), or 'done' to finish: ").strip().upper()
    if currency == 'DONE':
        break

    # Validate currency code first
    rate = get_exchange_rate_from_sheet(currency, "THB")
    while rate is None:
        print("Value not correct. Please enter a valid currency code.")
        currency = input("Enter source currency (e.g., USD), or 'done' to finish: ").strip().upper()
        if currency == 'DONE':
            break
        rate = get_exchange_rate_from_sheet(currency, "THB")
    if currency == 'DONE':
        break

    # Validate amount input
    while True:
        amount_input = input(f"Enter amount in {currency}: ")
        try:
            amount = float(amount_input)
            break
        except ValueError:
            print("Value not valid. Please enter a valid number.")

    currency_data.append((currency, amount, rate))

if currency_data:
    print_receipt(customer, currency_data)
else:
    print("No valid currency exchanges entered.")