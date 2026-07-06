import os
import re

root = os.path.abspath(".")

# 1. Rename semua file .htm -> .html
for folder, dirs, files in os.walk(root):
    for file in files:
        if file.lower().endswith(".htm"):
            old_path = os.path.join(folder, file)
            new_path = os.path.join(folder, file[:-4] + ".html")
            os.rename(old_path, new_path)
            print(f"Renamed: {old_path} -> {new_path}")

# 2. Update semua referensi .htm di file HTML
pattern = re.compile(r'(?i)\.htm(?=[?#"\'])')

for folder, dirs, files in os.walk(root):
    for file in files:
        if file.lower().endswith(".html"):
            path = os.path.join(folder, file)

            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            new_content = pattern.sub(".html", content)

            if content != new_content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated links: {path}")

print("Selesai.")