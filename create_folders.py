import os

main_folder = "asl_dataset"

classes = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + [
    "HELLO",
    "THANK_YOU",
    "GOOD_MORNING",
    "GOOD_NIGHT",
    "HOW_ARE_YOU",
    "I_LOVE_YOU",
    "WELCOME",
    "SORRY",
    "BYE"
]

os.makedirs(main_folder, exist_ok=True)

for name in classes:
    os.makedirs(os.path.join(main_folder, name), exist_ok=True)

print("Folders created!")