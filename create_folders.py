import os

main_folder = "asl_dataset"

classes = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") 

os.makedirs(main_folder, exist_ok=True)

for name in classes:
    os.makedirs(os.path.join(main_folder, name), exist_ok=True)

print("Folders created!")