import os
import re
import datetime
import xml.etree.ElementTree as ET
import minify_html
from csscompressor import compress
from rjsmin import jsmin

# Folder tempat script dijalankan
root = os.path.abspath(".")

# Domain website
DOMAIN = "https://tamannika.com"

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

# ===========================
# Perbaikan Canonical
# ===========================

canonical_pattern = re.compile(
    r'<link\s+rel=["\']canonical["\']\s+href=["\'][^"\']*["\']\s*/?>',
    re.IGNORECASE
)

# Statistik Canonical
fixed_canonical = 0
canonical_files = 0

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

# ===========================
# 3. Kompres Semua Gambar
# ===========================

from PIL import Image

print("\nMengompres gambar...")

compressed_images = 0
skipped_images = 0

total_before = 0
total_after = 0

SUPPORTED = (".jpg", ".jpeg", ".png")

for folder, dirs, files in os.walk(root):

    for file in files:

        if not file.lower().endswith(SUPPORTED):
            continue

        path = os.path.join(folder, file)

        try:

            before = os.path.getsize(path)

            img = Image.open(path)

            # Hilangkan metadata EXIF
            data = list(img.getdata())
            clean = Image.new(img.mode, img.size)
            clean.putdata(data)

            temp_path = path + ".tmp"

            if file.lower().endswith((".jpg", ".jpeg")):

                clean.save(
                    temp_path,
                    format="JPEG",
                    quality=65,
                    optimize=True,
                    progressive=True
                )

            elif file.lower().endswith(".png"):

                clean.save(
                    temp_path,
                    format="PNG",
                    optimize=True
                )

            after = os.path.getsize(temp_path)

            if after < before:

                os.replace(temp_path, path)

                compressed_images += 1

                total_before += before
                total_after += after

                print(
                    f"Compressed: {file} "
                    f"({before/1024:.0f} KB -> {after/1024:.0f} KB)"
                )

            else:

                os.remove(temp_path)
                skipped_images += 1

        except Exception as e:

            print(f"Gagal: {path}")
            print(e)


# ===========================
# 4. Minify HTML CSS JS
# ===========================
html_minified = 0
css_minified = 0
js_minified = 0
for folder, dirs, files in os.walk(root):

    for file in files:

        if not file.lower().endswith(".html"):
            continue

        path = os.path.join(folder, file)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        html = minify_html.minify(
            html,
            keep_comments=False,
            minify_css=True,
            minify_js=True
        )

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        html_minified += 1
        print("Minified HTML:", file)

for folder, dirs, files in os.walk(root):

    for file in files:

        if not file.lower().endswith(".css"):
            continue

        path = os.path.join(folder, file)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            css = f.read()

        css = compress(css)

        with open(path, "w", encoding="utf-8") as f:
            f.write(css)

        css_minified += 1
        print("Minified CSS:", file)

for folder, dirs, files in os.walk(root):

    for file in files:

        if not file.lower().endswith(".js"):
            continue

        path = os.path.join(folder, file)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            js = f.read()

        js = jsmin(js)

        with open(path, "w", encoding="utf-8") as f:
            f.write(js)

        css_minified += 1
        print("Minified JS:", file)

# ===========================
# 5. Generate sitemap.xml
# ===========================

urlset = ET.Element(
    "urlset",
    xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
)

sitemap_urls = 0

for folder, dirs, files in os.walk(root):

    # Folder yang tidak perlu dimasukkan sitemap
    dirs[:] = [
        d for d in dirs
        if d not in (
            ".git",
            ".github",
            "__pycache__",
            "wp-content",
            "wp-admin",
            "wp-includes"
        )
    ]

    for file in files:

        if file.lower() != "index.html":
            continue

        path = os.path.join(folder, file)

        rel_path = os.path.relpath(path, root).replace("\\", "/")

        if rel_path == "index.html":
            url = DOMAIN + "/"
        else:
            url = DOMAIN + "/" + os.path.dirname(rel_path).replace("\\", "/") + "/"

        url_element = ET.SubElement(urlset, "url")

        ET.SubElement(url_element, "loc").text = url

        lastmod = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(path)
        ).strftime("%Y-%m-%dT%H:%M:%S+00:00")

        ET.SubElement(url_element, "lastmod").text = lastmod

        sitemap_urls += 1

tree = ET.ElementTree(urlset)

ET.indent(tree, space="    ", level=0)

tree.write(
    os.path.join(root, "sitemap.xml"),
    encoding="utf-8",
    xml_declaration=True
)

print("\n===================================")
print("Selesai!")
print(f"File .htm di-rename                : {renamed_files}")
print(f"Link rel icon diperbarui           : tamannika.com ditambah ke url")
print(f"File HTML diperbarui               : {updated_files}")
print(f"URL localhost/.local diganti       : {replaced_urls}")
print(f"Google Tag diperbaiki              : {fixed_gtag} referensi")
print(f"File yang berisi perubahan GTAG    : {gtag_files} file")
print(f"Canonical diperbaiki               : {fixed_canonical} referensi")
print(f"File yang canonical diperbaiki     : {canonical_files} file")
print("Tujuan URL                          : https://tamannika.com/")
print(f"Gambar dikompres                   : {compressed_images}")
print(f"Gambar dilewati                    : {skipped_images}")
print(f"Ukuran sebelum                     : {total_before/1024/1024:.2f} MB")
print(f"Ukuran sesudah                     : {total_after/1024/1024:.2f} MB")
print(f"Penghematan                        : {(total_before-total_after)/1024/1024:.2f} MB")
print(f"HTML diminify                      : {html_minified}")
print(f"CSS diminify                       : {css_minified}")
print(f"JS diminify                        : {js_minified}")
print(f"Sitemap dibuat                     : sitemap.xml")
print(f"Jumlah URL dalam sitemap           : {sitemap_urls}")
print("===================================")