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
    "https://tamannikalokal.local/": "https://tamannika.com/",

    'href="wp-content/uploads/2025/07/cropped-logo-tamannika-e1751592306709-32x32.jpeg"':
    'href="https://tamannika.com/wp-content/uploads/2025/07/cropped-logo-tamannika-e1751592306709-32x32.jpeg"',

    'href="wp-content/uploads/2025/07/cropped-logo-tamannika-e1751592306709-192x192.jpeg"':
    'href="https://tamannika.com/wp-content/uploads/2025/07/cropped-logo-tamannika-e1751592306709-192x192.jpeg"',
}

# ===========================
# Perbaikan Google Tag / GA4
# ===========================

gtag_pattern = re.compile(
    r'src=["\'][^"\']*gtag/js\?id=(G-[A-Z0-9]+)["\']'
)

updated_files = 0
replaced_urls = 0

# Statistik Google Tag
fixed_gtag = 0          # Total referensi yang diperbaiki
gtag_files = 0          # Jumlah file yang mengalami perbaikan GTAG

for folder, dirs, files in os.walk(root):
    for file in files:

        if file.lower().endswith(".html"):

            path = os.path.join(folder, file)

            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            new_content = pattern.sub(".html", content)

            # Ganti URL lama
            for old, new in replacements.items():

                count = new_content.count(old)

                if count > 0:
                    replaced_urls += count
                    new_content = new_content.replace(old, new)

            # Perbaiki Google Tag
            new_content, count_gtag = gtag_pattern.subn(
                r'src="https://www.googletagmanager.com/gtag/js?id=\1"',
                new_content
            )

            if count_gtag > 0:
                fixed_gtag += count_gtag
                gtag_files += 1

            # ===========================
            # Perbaiki Canonical
            # ===========================

            rel_path = os.path.relpath(path, root).replace("\\", "/")

            if rel_path == "index.html":
                canonical_url = DOMAIN + "/"
            else:
                canonical_url = DOMAIN + "/" + os.path.dirname(rel_path).replace("\\", "/") + "/"

            new_content, canonical_count = canonical_pattern.subn(
                f'<link rel="canonical" href="{canonical_url}" />',
                new_content
            )

            if canonical_count > 0:
                fixed_canonical += canonical_count
                canonical_files += 1

            # Simpan jika berubah
            if content != new_content:

                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                updated_files += 1
                print(f"Updated: {path}")


print("\n===================================")
print("Selesai!")
print(f"File .htm di-rename                : {renamed_files}")
print(f"File HTML diperbarui               : {updated_files}")
print(f"URL localhost/.local diganti       : {replaced_urls}")
print(f"Google Tag diperbaiki              : {fixed_gtag} referensi")
print(f"File yang berisi perubahan GTAG    : {gtag_files} file")
print(f"Canonical diperbaiki               : {fixed_canonical} referensi")
print(f"File yang canonical diperbaiki     : {canonical_files} file")
print("Tujuan URL                         : https://tamannika.com/")
print("===================================")