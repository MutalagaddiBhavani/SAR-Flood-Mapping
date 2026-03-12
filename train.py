import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib

# ---------------- LOAD DATA ---------------- #

df = pd.read_csv("flood_training_data.csv")

print("Dataset Preview:")
print(df.head())


# ---------------- FEATURES & LABEL ---------------- #

X = df[["rainfall", "river", "temp"]]
y = df["risk"]


# ---------------- ENCODE LABELS ---------------- #

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)


# ---------------- TRAIN TEST SPLIT ---------------- #

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,
    test_size=0.2,
    random_state=42
)


# ---------------- MODEL ---------------- #

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


# ---------------- TRAIN ---------------- #

model.fit(X_train, y_train)

print("\nModel training completed!")


# ---------------- TEST ---------------- #

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\nModel Accuracy:", accuracy)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# ---------------- SAVE MODEL ---------------- #

joblib.dump(model, "flood_risk_model.pkl")

print("\nModel saved as flood_risk_model.pkl")
