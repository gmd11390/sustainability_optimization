import sqlite3

def create_port_assignments_table():
    conn = sqlite3.connect('databases/network_data.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS port_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        network_id TEXT NOT NULL,
        zone_id INTEGER NOT NULL,
        port_id TEXT NOT NULL
    )
    """)

    # Populate the table with initial data (Example data, modify as needed)
    initial_data = [
        ('DEMO_NETWORK_ID', 1, 'DEMO-SERIAL'),
        ('DEMO_NETWORK_ID', 2, 'DEMO-SERIAL'),
        ('DEMO_NETWORK_ID', 3, 'DEMO-SERIAL'),
        ('DEMO_NETWORK_ID', 4, 'DEMO-SERIAL'),
    ]

    cursor.executemany("""
    INSERT INTO port_assignments (network_id, zone_id, port_id)
    VALUES (?, ?, ?)
    """, initial_data)

    conn.commit()
    conn.close()

create_port_assignments_table()