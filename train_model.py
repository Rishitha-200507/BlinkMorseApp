import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import json
import joblib

# Load CSV
df = pd.read_csv("sign_data.csv")

X = df.drop("target", axis=1).values
y = df["target"].values

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Save encoder
joblib.dump(le, "label_encoder.pkl")

label_map = {int(i): str(label) for i, label in enumerate(le.classes_)}

# ----------------------------
# Attention Neural Network
# ----------------------------
class AttentionModel(nn.Module):
    def __init__(self, input_size, num_classes):
        super().__init__()

        self.attn = nn.Sequential(
            nn.Linear(input_size, input_size),
            nn.Sigmoid()
        )

        self.fc = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(128, 64),
            nn.ReLU(),

            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        w = self.attn(x)
        x = x * w
        return self.fc(x)

# Train Attention Model
model = AttentionModel(X.shape[1], len(le.classes_))

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

X_tensor = torch.FloatTensor(X)
y_tensor = torch.LongTensor(y_encoded)

for epoch in range(100):

    optimizer.zero_grad()

    output = model(X_tensor)

    loss = criterion(output, y_tensor)

    loss.backward()

    optimizer.step()

    if (epoch+1) % 10 == 0:
        print(f"Epoch {epoch+1}: Loss {loss.item():.4f}")

torch.save(model.state_dict(), "attention_model.pth")

# ----------------------------
# XGBoost
# ----------------------------
print("\nTraining XGBoost...")

xgb = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    objective="multi:softprob",
    num_class=len(le.classes_)
)

xgb.fit(X, y_encoded)

xgb.save_model("xgboost_model.json")

# Save label map
with open("label_map.json", "w") as f:
    json.dump(label_map, f)

print("\nTraining Completed Successfully!")