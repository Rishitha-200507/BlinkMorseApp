import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import json

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("sign_data.csv")

X = df.drop("target", axis=1).values
y = df["target"].values

# -----------------------------
# Encode Labels
# -----------------------------
le = LabelEncoder()
y_encoded = le.fit_transform(y)

label_map = {int(i): str(label) for i, label in enumerate(le.classes_)}

# -----------------------------
# XGBoost Model
# -----------------------------
print("Training XGBoost...")

xgb_model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    objective="multi:softprob",
    num_class=len(le.classes_)
)

xgb_model.fit(X, y_encoded)
xgb_model.save_model("xgboost_model.json")

# -----------------------------
# Neural Network Model
# -----------------------------
class SignModel(nn.Module):
    def __init__(self, input_size, num_classes):
        super(SignModel, self).__init__()

        self.fc = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(128, 64),
            nn.ReLU(),

            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        return self.fc(x)


print("Training Neural Network...")

model = SignModel(X.shape[1], len(le.classes_))

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

X_tensor = torch.FloatTensor(X)
y_tensor = torch.LongTensor(y_encoded)

# -----------------------------
# Training Loop
# -----------------------------
for epoch in range(100):

    optimizer.zero_grad()

    outputs = model(X_tensor)

    loss = criterion(outputs, y_tensor)

    loss.backward()

    optimizer.step()

    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/100 Loss: {loss.item():.4f}")

# -----------------------------
# SAVE MODEL (FIXED ERROR HERE)
# -----------------------------
torch.save(model.state_dict(), "attention_model.pth")

# Save label map
with open("label_map.json", "w") as f:
    json.dump(label_map, f)

print("\n--- TRAINING COMPLETE ---")
print("Saved:")
print("xgboost_model.json")
print("attention_model.pth")
print("label_map.json")