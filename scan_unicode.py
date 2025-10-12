import os

def scan_for_unicode(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if any(ord(char) > 127 for char in line):
                            print(f"{file}, line {i}: {line.strip()}")

scan_for_unicode(".")
