import os
import glob

# Set to '.' to run in the current directory, or provide a specific path
folder_path = '.'

# Iterate through all .inp files in the folder
for filepath in glob.glob(os.path.join(folder_path, '*.txt')):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            # Read the first line and strip leading/trailing whitespace
            first_line = file.readline().strip()
            
            # Skip empty files
            if not first_line:
                print(f"Skipped: '{os.path.basename(filepath)}' is empty.")
                continue
                
            # Extract the first token (the number)
            number = first_line.split()[0]
            
        # Construct the new path
        directory = os.path.dirname(filepath)
        new_filename = f"n{number}.inp"
        new_filepath = os.path.join(directory, new_filename)
        
        # Prevent overwriting if a file with the target name already exists
        if not os.path.exists(new_filepath):
            os.rename(filepath, new_filepath)
            print(f"Renamed: '{os.path.basename(filepath)}' -> '{new_filename}'")
        else:
            print(f"Skipped: '{new_filename}' already exists.")
            
    except Exception as e:
        print(f"Error processing '{os.path.basename(filepath)}': {e}")