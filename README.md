# 🐍 WordPress JSON API CLI Tool

> **Wpjson Python CLI** — Fetch posts, categories, and media from WordPress REST API with ease.  
> *Python CLI yang lebih modern, ringan, dan mudah digunakan.*

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

---

## 📋 Daftar Isi

- [✨ Fitur](#-fitur)
- [📦 Persyaratan](#-persyaratan)
- [🚀 Instalasi](#-instalasi)
- [⚡ Penggunaan Cepat](#-penggunaan-cepat)
- [📖 Referensi CLI](#-referensi-cli)
- [⚙️ Konfigurasi](#-konfigurasi)
- [📁 Struktur Output](#-struktur-output)
- [🧩 Contoh JSON Output](#-contoh-json-output)
- [🔧 Penggunaan sebagai Module](#-penggunaan-sebagai-module)
- [🌍 Localization & Unicode](#-localization--unicode)
- [🐛 Troubleshooting](#-troubleshooting)
- [🤝 Kontribusi](#-kontribusi)
- [📄 Lisensi](#-lisensi)

---

## ✨ Fitur

✅ **Multi-Action CLI**  
   - Fetch categories, posts by category, atau single post by URL

✅ **Image Downloader**  
   - Download featured media + semua gambar dalam konten secara otomatis

✅ **Link Replacement**  
   - Ganti semua link dari target WordPress ke website Anda

✅ **JSON Output**  
   - Hasil dalam format JSON yang rapi, siap untuk import ke sistem lain

✅ **SEO-Friendly Slug Generator**  
   - Fungsi `seofy()` dan `cleanText()` untuk sanitasi teks

✅ **Error Handling**  
   - Handle timeout, SSL, dan network errors dengan graceful

✅ **Progress Output**  
   - Feedback real-time saat proses fetch/download (bisa dimatikan dengan `--quiet`)

✅ **Cross-Platform**  
   - Berjalan di Windows, macOS, dan Linux

---

## 📦 Persyaratan

| Komponen | Versi Minimum |
|----------|--------------|
| Python | 3.8+ |
| requests | 2.28.0+ |
| pip | 20.0+ |

### Install Dependencies

```bash
# Clone atau download script
git clone https://github.com/ahmadsopyan9/Wpjson-Python-CLI.git
cd Wpjson-Python-CLI

# Install dependencies
pip install -r requirements.txt
```

> 💡 **Opsional**: Untuk transliterasi Unicode yang lebih akurat (misal: "Café" → "cafe"):
> ```bash
> pip install unidecode
> ```

---

## 🚀 Instalasi

### Cara 1: Clone Repository
```bash
git clone https://github.com/ahmadsopyan9/Wpjson-Python-CLI.git
cd Wpjson-Python-CLI
pip install -r requirements.txt
chmod +x wpjson.py
```

### Cara 2: Download Langsung
```bash
curl -O https://raw.githubusercontent.com/ahmadsopyan9/Wpjson-Python-CLI/main/wpjson.py
pip install requests
chmod +x wpjson.py
```

### Cara 3: Install via pip 
```bash
pip install wpjson-cli
```

### Verifikasi Instalasi
```bash
python wpjson.py --help
# atau
./wpjson.py --help
```

---

## ⚡ Penggunaan Cepat

### 🔹 Fetch Semua Kategori
```bash
python wpjson.py -t https://example.com -c
```

### 🔹 Fetch Posts dari Kategori Tertentu
```bash
# Kategori ID 5, halaman 1, 10 items
python wpjson.py -t https://example.com -p 5

# Dengan pagination
python wpjson.py -t https://example.com -p 5 --page 2 --per-page 20
```

### 🔹 Save Single Post by URL
```bash
python wpjson.py -t https://example.com \
  -s "https://example.com/wp-json/wp/v2/posts/123" \
  -C 5
```

### 🔹 Download Gambar + Ganti Link
```bash
python wpjson.py -t https://example.com \
  -p 3 \
  -d \
  -r https://mysite.com \
  -o my_output
```

### 🔹 Output ke Stdout Saja (Tanpa Save File)
```bash
python wpjson.py -t https://example.com -c --no-save | jq '.[0].name'
```

### 🔹 Mode Quiet (Minimal Output)
```bash
python wpjson.py -t https://example.com -p 1 -q
```

---

## 📖 Referensi CLI

### 🔧 Arguments Utama

| Argument | Short | Type | Default | Deskripsi |
|----------|-------|------|---------|-----------|
| `--target` | `-t` | `str` | *required* | URL WordPress target (tanpa `/wp-json`) |
| `--categories` | `-c` | `flag` | - | Fetch semua kategori |
| `--category-posts` | `-p` | `int` | - | Fetch posts dari kategori ID tertentu |
| `--save-post` | `-s` | `str` | - | Save single post dari WP JSON API URL |
| `--category-id` | `-C` | `int` | `1` | Category ID untuk action `--save-post` |
| `--page` | - | `int` | `1` | Nomor halaman untuk pagination |
| `--per-page` | - | `int` | `10` | Jumlah items per halaman (max 100 untuk WP API) |
| `--download-images` | `-d` | `flag` | `false` | Download featured media + gambar dalam konten |
| `--replace-link` | `-r` | `str` | - | Ganti URL target dengan URL website Anda |
| `--output-dir` | `-o` | `str` | `"output"` | Nama direktori output |
| `--no-save` | - | `flag` | `false` | Jangan simpan ke file JSON (stdout only) |
| `--quiet` | `-q` | `flag` | `false` | Suppress progress messages |
| `--help` | `-h` | - | - | Tampilkan bantuan |

### 🔹 Contoh Kombinasi Advanced

```bash
# Batch fetch multiple categories
for id in 1 2 3 4 5; do
  python wpjson.py -t https://example.com -p $id --page 1 --per-page 50 -d
done

# Fetch dengan custom output + link replacement
python wpjson.py -t https://oldsite.com \
  -p 10 \
  --page 1 \
  --per-page 100 \
  -d \
  -r https://newsite.com \
  -o migration_data \
  --no-save | jq '.[] | {title, slug, category_id}'

# Pipeline ke tool lain
python wpjson.py -t https://example.com -c --no-save | \
  python process_categories.py
```

---

## ⚙️ Konfigurasi

### Via CLI Arguments (Recommended)
Semua konfigurasi bisa diatur via command-line arguments seperti dijelaskan di atas.

### Via Code (Jika digunakan sebagai module)
```python
from wpjson import Wpjson

config = {
    "targetUrl": "https://example.com",
    "downloadImage": True,
    "myWebsiteLink": "https://mysite.com",
    "dirOutputName": "my_output",
    "saveFileJson": True
}

wp = Wpjson(config)
wp.build_data_post_category(ctg_id=5, page=1, per_page=20)
result = wp.response_object()
```

### Environment Variables (Opsional)
```bash
export WPJSON_TARGET="https://example.com"
export WPJSON_OUTPUT_DIR="production_data"
export WPJSON_DOWNLOAD_IMAGES="true"

python wpjson.py -c
```

---

## 📁 Struktur Output

```
output/                          # Default: --output-dir
├── images/                      # Semua gambar yang didownload
│   ├── featured-image-123.jpg
│   ├── content-photo.png
│   └── screenshot_2024.webp
│
└── tmp/                         # File JSON hasil fetch
    ├── post_ctg_5_page_1_limit_10.json
    ├── post_ctg_5_page_2_limit_10.json
    └── my-awesome-post-slug.json   # Hasil dari --save-post
```

### 📄 Format JSON Output

#### 📌 Kategori Response
```json
[
  {
    "id": 5,
    "count": 42,
    "description": "Technology news and tutorials",
    "link": "https://example.com/category/tech",
    "name": "Technology",
    "slug": "tech",
    "taxonomy": "category",
    "parent": 0
  }
]
```

#### 📌 Post Response (dari `build_data_post_category` / `save_post`)
```json
{
  "author_id": 1,
  "title": "Judul Artikel Lengkap Di Sini",
  "slug": "judul-artikel-lengkap-di-sini",
  "featured_media": "featured-image-123.jpg",
  "summary": "<p>Ringkasan artikel dalam HTML...</p>",
  "content": "<p>Konten lengkap dengan gambar dan formatting...</p>",
  "category_id": 5,
  "wp_featured_media_url": "https://example.com/wp-content/uploads/2024/01/image.jpg",
  "wp_categories": [5, 12, 23],
  "wp_tags": [45, 67, 89],
  "status": "publish",
  "all_image_content": [
    "https://example.com/wp-content/uploads/2024/01/img1.jpg",
    "https://example.com/wp-content/uploads/2024/01/img2.png"
  ]
}
```

---

## 🧩 Penggunaan sebagai Module

`wpjson.py` bisa di-import ke project Python lain:

```python
# example_usage.py
from wpjson import Wpjson
import json

# Inisialisasi
wp = Wpjson({
    "targetUrl": "https://example.com",
    "downloadImage": True,
    "myWebsiteLink": "https://mysite.com"
})

# Fetch categories
categories = wp.get_all_category(page=1, per_page=100).response_object()
print(f"Found {len(categories)} categories")

# Fetch posts from category
posts = wp.build_data_post_category(ctg_id=5, page=1, per_page=20).response_object()
print(f"Fetched {len(posts)} posts")

# Process data
for post in posts:
    print(f"📝 {post['title']}")
    print(f"🖼️  Featured: {post['featured_media']}")
    print(f"🔗 Images: {len(post['all_image_content'])} found\n")

# Output to custom file
with open('custom_output.json', 'w', encoding='utf-8') as f:
    json.dump(posts, f, indent=2, ensure_ascii=False)
```

---

## 🌍 Localization & Unicode

### 🇮🇩 Indonesian Content Support
Tool ini mendukung penuh konten berbahasa Indonesia:

```bash
# Fetch posts dengan judul & konten bahasa Indonesia
python wpjson.py -t https://blogindonesia.com -p 3 -d

# Output akan mempertahankan karakter Unicode
# Contoh: "Mengenal Python untuk Pemula" → slug: "mengenal-python-untuk-pemula"
```

### 🔤 Transliterasi Unicode
Fungsi `seofy()` dan `clean_text()` menangani:
- Karakter khusus: `é → e`, `ñ → n`, `ü → u`
- Emoji & simbol: dihapus otomatis
- Spasi berlebih: dinormalisasi

> 💡 **Tips**: Install `unidecode` untuk hasil transliterasi lebih akurat:
> ```python
> # Di wpjson.py, ganti:
> # from unicodedata import normalize
> from unidecode import unidecode
> 
> # Lalu di fungsi _seofy dan _clean_text:
> s_string = unidecode(s_string)
> ```

---

## 🐛 Troubleshooting

### ❌ "targetUrl Config is Required!"
```bash
# Pastikan flag -t / --target diisi
python wpjson.py -t https://example.com -c  # ✅ Benar
python wpjson.py -c                          # ❌ Salah
```

### ❌ "SSL Certificate Verify Failed"
```bash
# Opsi 1: Update certificates
pip install --upgrade certifi

# Opsi 2: (Tidak direkomendasikan untuk production) Skip SSL verify
# Edit wpjson.py, tambahkan verify=False di requests.get()
```

### ❌ "404 Not Found" pada WP API
```bash
# Pastikan:
# 1. URL target benar (tanpa /wp-json di akhir)
# 2. WordPress REST API aktif (biasanya aktif default di WP 4.7+)
# 3. Tidak ada plugin security yang memblokir API

# Test API manual:
curl https://example.com/wp-json/wp/v2/posts?per_page=1
```

### ❌ Gambar Tidak Terdownload
```bash
# Cek:
# 1. URL gambar publicly accessible (tidak butuh login)
# 2. Server target tidak memblokir user-agent / hotlinking
# 3. Cukup ruang disk di folder output/images/

# Debug: Tambahkan print di fungsi _download_single_image()
```

### ❌ Output JSON Berantakan / Encoding Error
```bash
# Pastikan terminal mendukung UTF-8
# Windows: chcp 65001
# Linux/macOS: export LANG=en_US.UTF-8

# Atau redirect ke file:
python wpjson.py -t https://example.com -c --no-save > output.json
```

---

## 🤝 Kontribusi

Kami sangat terbuka untuk kontribusi! 🎉

### 🔄 Cara Berkontribusi
1. Fork repository ini
2. Buat feature branch: `git checkout -b fitur-keren`
3. Commit perubahan: `git commit -m '✨ Tambah fitur keren'`
4. Push ke branch: `git push origin fitur-keren`
5. Buka Pull Request

### 🧪 Testing
```bash
# Install dev dependencies (jika ada)
pip install pytest requests-mock

# Jalankan test (jika tersedia)
pytest tests/

# Lint code
flake8 wpjson.py
black wpjson.py --check
```

### 📝 Guidelines
- Gunakan type hints untuk fungsi publik
- Tambahkan docstring untuk fungsi baru
- Maintain kompatibilitas Python 3.8+
- Update dokumentasi jika mengubah behavior

---

## 📄 Lisensi

Distributed under **MIT License**. Lihat [`LICENSE`](LICENSE) untuk informasi lengkap.

```
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
...
```

---

## 🙏 Terima Kasih

Terima kasih untuk:
- 🌐 Komunitas WordPress untuk REST API yangawesome
- 🐍 Komunitas Python untuk ekosistem yang luar biasa
- 💻 Semua contributor yang telah membantu pengembangan tool ini

---

> 🇮🇩 **Dibuat dengan ❤️ untuk developer Indonesia**  
> *Semoga tool ini membantu migrasi, backup, atau integrasi WordPress Anda menjadi lebih mudah!*

---

**🔗 Links Penting**
- [WordPress REST API Handbook](https://developer.wordpress.org/rest-api/)
- [Python Requests Documentation](https://docs.python-requests.org/)
- [Argparse Tutorial](https://docs.python.org/3/howto/argparse.html)

**📬 Contact**  
Punya pertanyaan, bug report, atau feature request?  
👉 Buka [Issue](https://github.com/yourusername/wpjson-python/issues) atau DM saya!

---

<div align="center">

**⭐ Jangan lupa star repository ini jika membantu!** ⭐

</div>
