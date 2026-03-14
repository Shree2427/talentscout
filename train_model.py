import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib

df = pd.read_csv("interview_dataset.csv")

X = df[['Experience','Tech_Count','Avg_Score']]
y = df['Final_Decision']

# Check if dataset has both classes
if y.nunique() < 2:
    print("Error: Dataset must contain both 0 and 1 classes.")
    exit()

model = LogisticRegression()
model.fit(X, y)

joblib.dump(model, "hiring_model.pkl")

print("✅ Model trained and saved successfully!")