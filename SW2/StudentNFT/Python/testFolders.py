from pathlib import Path

# Get the current script folder (where your script is running)
base_dir = Path(__file__).parent.resolve()

imageFolder = "certificates"
pngFile = "PitchMaster.png"
# Construct the path to images/a.png
image_path = base_dir / imageFolder / pngFile

# Use the path safely
print(image_path)               # For display
print(str(image_path))         # When passing to open(), requests, etc.

# Example: open the file
with open(image_path, 'rb') as f:
    data = f.read()
    print(data)