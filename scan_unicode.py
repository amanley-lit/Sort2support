import os
import sys

def scan_for_unicode(path):
    for root, dirs, files in os.walk(path):
        # Skip virtualenv and cache folders
        if "venv" in root or "__pycache__" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            if any(ord(char) > 127 for char in line):
                                unicode_chars = [char for char in line if ord(char) > 127]
                                print(f"{file}, line {i}: {line.strip()} → Unicode: {''.join(unicode_chars)}")
                except Exception as e:
                    print(f"Error reading {full_path}: {e}")

# Use CLI argument if provided, else default to current directory
scan_for_unicode(sys.argv[1] if len(sys.argv) > 1 else ".")
