import os
import re

# Folder tempat script dijalankan
root = os.path.abspath(".")

# ===========================
# 1. Rename semua file .htm -> .html
# ===========================

renamed_files = 0

for folder, dirs, files in os.walk(root):
    for file in files:
        if file.lower().endswith(".htm"):
            old_path = os.path.join(folder, file)
            new_path = os.path.join(folder, file[:-4] + ".html")

            os.rename(old_path, new_path)

            renamed_files += 1
            print(f"Renamed: {old_path} -> {new_path}")

# ===========================
# 2. Update isi file HTML
# ===========================

pattern = re.compile(r'(?i)\.htm(?=[?#"\'])')

replacements = {
    "http://localhost:10004/": "https://tamannika.com/",
    "http://tamannikalokal.local/": "https://tamannika.com/",
}

updated_files = 0

for folder, dirs, files in os.walk(root):
    for file in files:
        if file.lower().endswith(".html"):

            path = os.path.join(folder, file)

            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            new_content = pattern.sub(".html", content)

            # Ganti semua URL
            for old, new in replacements.items():
                new_content = new_content.replace(old, new)

            if content != new_content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                updated_files += 1
                print(f"Updated: {path}")

print("\n===================================")
print("Selesai!")
print(f"File .htm di-rename : {renamed_files}")
print(f"File HTML diperbarui: {updated_files}")
print("===================================")