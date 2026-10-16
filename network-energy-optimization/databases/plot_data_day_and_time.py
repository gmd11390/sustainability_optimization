import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def fetch_data(db_path):
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM motion_events"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def prepare_data(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['hour'] = df['timestamp'].dt.hour
    return df

def plot_data(df, zone_id):
    zone_df = df[df['zone_id'] == zone_id]
    grouped = zone_df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
    
    # Reorder the days of the week
    ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    grouped = grouped.reindex(ordered_days)
    
    # Plotting
    fig, ax = plt.subplots(figsize=(20, 10))
    width = 0.04  # Width of each bar
    positions = [i for i in range(len(ordered_days))]
    
    for hour in range(24):
        offset_positions = [pos + (hour * width) for pos in positions]
        ax.bar(offset_positions, grouped[hour], width=width, label=f'{hour}:00 - {hour+1}:00')
    
    ax.set_title(f'Zone {zone_id} - Motion Events by Hour and Day of the Week')
    ax.set_xlabel('Day of the Week')
    ax.set_ylabel('Number of Events')
    ax.set_xticks([pos + 0.5 for pos in positions])
    ax.set_xticklabels(ordered_days)
    ax.legend(title='Hour of the Day', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    db_path = 'databases/simulated_data_new_july10.db'
    df = fetch_data(db_path)
    df = prepare_data(df)
    
    for zone_id in df['zone_id'].unique():
        plot_data(df, zone_id)

if __name__ == "__main__":
    main()