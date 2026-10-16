import sqlite3
import random
import datetime

def generate_motion_events(db_path, num_entries=10000):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create motion_events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS motion_events (
            id INTEGER PRIMARY KEY,
            network_id TEXT,
            zone_id INTEGER,
            motion INTEGER,
            timestamp TIMESTAMP
        )
    """)

    network_id = "L_1234567890"
    start_date = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2024, 1, 1)
    total_days = (end_date - start_date).days
    events_per_day = num_entries // total_days
    extra_events = num_entries % total_days
    data = []

    for day in range(total_days):
        current_date = start_date + datetime.timedelta(days=day)
        num_events_today = events_per_day + (1 if day < extra_events else 0)
        
        for _ in range(num_events_today):
            timestamp = current_date + datetime.timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
            weekday = timestamp.weekday()
            hour = timestamp.hour

            zone_id = random.choices([1, 2, 3, 4], [0.25, 0.25, 0.25, 0.25])[0]

            if zone_id == 1:
                if 8 <= hour < 19 and weekday < 5:
                    motion = random.choices([0, 1], [0.3, 0.7])[0]
                else:
                    motion = random.choices([0, 1], [0.7, 0.3])[0]
            elif zone_id == 2:
                if weekday < 5 and 8 <= hour < 19:
                    motion = random.choices([0, 1], [0.4, 0.6])[0]
                else:
                    motion = 0
            elif zone_id == 3:
                if weekday == 4:  # Fridays
                    motion = 0
                elif weekday == 5 and 12 <= hour < 17:  # Saturdays 12pm-5pm
                    motion = random.choices([0, 1], [0.1, 0.9])[0]
                else:
                    motion = random.choices([0, 1], [0.7, 0.3])[0]
            elif zone_id == 4:
                if weekday in [0, 2, 4] and 21 <= hour < 22:  # Mon, Wed, Fri from 9pm to 10pm
                    motion = random.choices([0, 1], [0.1, 0.9])[0]
                else:
                    motion = 0

            data.append((network_id, zone_id, motion, timestamp))

    cursor.executemany("INSERT INTO motion_events (network_id, zone_id, motion, timestamp) VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

# Specify the path to your new database
db_path = 'databases/simulated_data_new_july10.db'
generate_motion_events(db_path)