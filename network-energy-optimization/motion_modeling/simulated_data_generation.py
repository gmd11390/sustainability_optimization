import sqlite3
import random
import datetime

# Connect to SQLite database
conn = sqlite3.connect('simulated_network_data.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY,
        network_id TEXT,
        zone_id INTEGER,
        motion INTEGER,
        timestamp TEXT
    )
''')

# Function to generate random timestamps within a given range
def random_date(start, end):
    return start + datetime.timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())),
    )

# Define time range for data generation
start_date = datetime.datetime(2023, 1, 1)
end_date = datetime.datetime(2023, 12, 31)

# Define zones and their respective motion probabilities
zones = {
    1: 0.30,
    2: 0.10,
    3: 0.58,
    4: 0.02
}

# Generate periods of time with no motion each week
no_motion_hours_per_day = 5
no_motion_start_hour = 0  # Midnight

# Generate data
data = []
current_date = start_date
while current_date <= end_date:
    # Determine if current hour falls within the no motion period for the day
    in_no_motion_period = no_motion_start_hour <= current_date.hour < (no_motion_start_hour + no_motion_hours_per_day)

    for zone_id, motion_prob in zones.items():
        motion = 0 if in_no_motion_period else int(random.random() < motion_prob)
        data.append((
            f"Network_{random.randint(1, 5)}",  # Random network_id
            zone_id,
            motion,
            current_date.strftime("%Y-%m-%d %H:%M:%S")
        ))

    # Move to the next hour
    current_date += datetime.timedelta(hours=1)

# Insert data into the database
c.executemany('''
    INSERT INTO events (network_id, zone_id, motion, timestamp)
    VALUES (?, ?, ?, ?)
''', data)

# Commit and close
conn.commit()
conn.close()

print("Data generation complete.")