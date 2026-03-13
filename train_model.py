import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib

# Load dataset
df = pd.read_csv("interview_dataset.csv")

X = df[['Experience', 'Tech_Count', 'Avg_Score']]
y = df['Final_Decision']

# Train model
model = LogisticRegression()
model.fit(X, y)

# Save model
joblib.dump(model, "hiring_model.pkl")

print("✅ Model trained and saved successfully!")