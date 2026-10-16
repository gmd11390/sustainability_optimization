import sqlite3
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# Load the data from the SQLite database
conn = sqlite3.connect('simulated_network_data.db')
df = pd.read_sql_query("SELECT * FROM events", conn)
conn.close()

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Extract features from timestamp
df['hour'] = df['timestamp'].dt.hour
df['day'] = df['timestamp'].dt.day
df['month'] = df['timestamp'].dt.month
df['weekday'] = df['timestamp'].dt.weekday

# Define features and target variable
X = df[['network_id', 'zone_id', 'hour', 'day', 'month', 'weekday']]
y = df['motion']

# Preprocessing pipeline
categorical_features = ['network_id']
numerical_features = ['zone_id', 'hour', 'day', 'month', 'weekday']
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(), categorical_features)
    ])

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Transform the data
X_train = preprocessor.fit_transform(X_train)
X_test = preprocessor.transform(X_test)

# Load the trained model
model = tf.keras.models.load_model('motion_detection_model.h5')

# Make predictions
y_pred = model.predict(X_test)

# Convert predictions to binary values
y_pred_binary = (y_pred > 0.5).astype(int)

# Evaluate the model
print("Classification Report:")
print(classification_report(y_test, y_pred_binary))

print("Confusion Matrix:")
conf_matrix = confusion_matrix(y_test, y_pred_binary)
print(conf_matrix)