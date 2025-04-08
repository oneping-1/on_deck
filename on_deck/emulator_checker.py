import os

use_emulator = False

# Get the directory of the current file
current_dir = os.path.dirname(__file__)
# Go one folder up
parent_dir = os.path.dirname(current_dir)
use_emulator_path = os.path.join(parent_dir, "USE_EMULATOR.txt")

if os.path.exists(use_emulator_path):
    with open(use_emulator_path, encoding='utf-8') as f:
        use_emulator = f.read().strip().lower() == "true"
else:
    # Create the file with default content "false"
    with open(use_emulator_path, "w", encoding='utf-8') as f:
        f.write("false")
    print(f"'{use_emulator_path}' not found. Created with default value 'false'.")
    use_emulator = False

def is_emulator():
    """
    Check if the emulator is being used.
    This function checks if the emulator is being used by looking for a
    specific file in the parent directory. If the file is found and its
    content is "true", it returns True. Otherwise, it returns False.
    The file is expected to be named "USE_EMULATOR.txt" and should be
    located in the parent directory of the current file.
    The content of the file should be "true" (case insensitive) to

    Returns:
        bool: True if the emulator is being used, False otherwise.
    """
    if use_emulator:
        return True
    return False
