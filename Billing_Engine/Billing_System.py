
# import csv
# from datetime import datetime
# import calendar
# rows=[]
# prices=[]
# with open("Plans.csv","r") as file:
#     reader=csv.DictReader(file)
#     for row in reader:
#         rows.append(row)
# with open("Price.csv","r") as file:
#     reader=csv.DictReader(file)
#     for row in reader:
#         prices.append(row)
# customer_data = []

# for i in range(len(rows)):
#     for j in range(i + 1, len(rows)):
#         customer_id_row = rows[i]
#         customer_id_row_second = rows[j]

#         if customer_id_row["customer_id"] == customer_id_row_second["customer_id"]:
#             related_list = [rows[i], rows[j]]
#             customer_data.append(related_list)

# price_per_id = {}

# for row in customer_data:
#     if len(row) == 1:
#         event = row[0]
#         date = datetime.strptime(event["event_date"], "%Y-%m-%d").date()

#         if date.year == 2026 and date.month == 9:
#             start_day = date.day
#             end_day = calendar.monthrange(date.year, date.month)[1]
#             total_days = end_day - start_day + 1

#             plan_code = event["plan_code"]

#             for p in prices:
#                 if p["plan_code"] == plan_code:
#                     price = float(p["monthly_fee"])
#                     break
#             else:
#                 price = 0

#             total_cost = (total_days / end_day) * price
#             price_per_id[event["customer_id"]] = round(total_cost, 2)

#     else{

#     }

import csv
from datetime import datetime
import calendar
import sqlite3

rows = []
prices = []

with open("Plans.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        rows.append(row)

with open("Price.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        prices.append(row)
customer_data = []
for i in range(len(rows)):
    found = False
    for j in range(len(customer_data)):
        if customer_data[j][0]["customer_id"] == rows[i]["customer_id"]:
            customer_data[j].append(rows[i])
            found = True
            break
    if found == False:
        customer_data.append([rows[i]])

price_per_id = {}
for group in customer_data:
    for i in range(len(group)):
        for j in range(i + 1, len(group)):
            if group[i]["event_date"] > group[j]["event_date"]:
                temp = group[i]
                group[i] = group[j]
                group[j] = temp

    customer_id = group[0]["customer_id"]
    end_day = calendar.monthrange(2026, 9)[1]
    total_cost = 0
    segment1 = 0
    segment2 = 0
    active_plan = ""

    for event in group:
        date = datetime.strptime(event["event_date"], "%Y-%m-%d").date()
        if date < datetime(2026, 9, 1).date():
            if event["event_type"] == "CANCEL":
                active_plan = ""
            else:
                active_plan = event["plan_code"]

    period_start = 1
    september_events = False

    for event in group:
        date = datetime.strptime(event["event_date"], "%Y-%m-%d").date()
        if date.year == 2026 and date.month == 9:
            september_events = True
            event_day = date.day

            if active_plan != "":
                for p in prices:
                    if p["plan_code"] == active_plan:
                        price = float(p["monthly_fee"])
                        break
                else:
                    price = 0

                if event_day > period_start:
                    segment1 += ((event_day - period_start) / end_day) * price

            if event["event_type"] == "CANCEL":
                active_plan = ""
            else:
                active_plan = event["plan_code"]

            period_start = event_day

    if not september_events:
        continue

    if active_plan != "":
        for p in prices:
            if p["plan_code"] == active_plan:
                price = float(p["monthly_fee"])
                break
        else:
            price = 0

        segment2 += ((end_day - period_start + 1) / end_day) * price

    total_cost = segment1 + segment2

    if total_cost > 0:
        data = [round(segment1, 2), round(segment2, 2), round(total_cost, 2)]
        price_per_id[customer_id] = data
conn = sqlite3.connect("billing.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS billing (
    Customer_id TEXT PRIMARY KEY,
    segment1_Price REAL DEFAULT 0,
    segment2_Price REAL DEFAULT 0,
    Total_Price REAL DEFAULT 0
)
""")
for group in customer_data:
    customer_id = group[0]["customer_id"]
    segment1, segment2, total_cost = price_per_id.get(customer_id, [0, 0, 0])

    cursor.execute("""
    INSERT  INTO billing
    (Customer_id, segment1_Price, segment2_Price, Total_Price)
    VALUES (?, ?, ?, ?)
    """, (customer_id, segment1, segment2, total_cost))

conn.commit()

cursor.execute("SELECT * FROM billing")
for row in cursor.fetchall():
    print(row)

conn.close()



            


    


