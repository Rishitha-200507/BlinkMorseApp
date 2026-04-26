import os
import shutil

# Where your images are currently sitting
DATA_DIR = './asl_dataset'

print("--- Auto-Organizing your Images ---")

# Get list of all files in the folder
files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]

for filename in files:
    # Take the first letter of the filename (e.g., 'A' from 'A.jpg.jpeg')
    letter = filename[0].upper()
    
    if letter.isalpha():
        # Create the subfolder path (e.g., ./asl_dataset/A)
        new_folder = os.path.join(DATA_DIR, letter)
        
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)
            print(f"Created folder: {letter}")
            
        # Move the file into the folder
        old_path = os.path.join(DATA_DIR, filename)
        new_path = os.path.join(new_folder, filename)
        shutil.move(old_path, new_path)
        print(f"Moved {filename} -> folder {letter}")

print("\nDONE! Your folders are ready.")