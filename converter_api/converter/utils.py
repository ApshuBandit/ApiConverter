import os
import io
import zipfile
import fitz  # PyMuPDF
from PIL import Image


def pdf_to_images_and_html(pdf_file, output_dir, image_format, zip_path):
    """
    Конвертирует PDF в изображения + HTML и упаковывает в ZIP.

    :param pdf_file: PDF-файл (UploadedFile или file-like)
    :param output_dir: временная папка для работы
    :param image_format: формат изображений ("jpg", "png", "webp")
    :param zip_path: путь к итоговому .zip
    """

    # Папка для картинок
    img_folder = os.path.join(output_dir, "img")
    os.makedirs(img_folder, exist_ok=True)

    # Загружаем PDF
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    image_paths = []

    # Проходим по страницам
    for page_number in range(doc.page_count):
        page = doc.load_page(page_number)
        mat = fitz.Matrix(2, 2)  # масштаб = качество
        pix = page.get_pixmap(matrix=mat)

        image_name = f"{page_number + 1}.{image_format}"
        image_path = os.path.join(img_folder, image_name)

        if image_format.lower() == "webp":
            img_data = pix.tobytes("png")
            pil_image = Image.open(io.BytesIO(img_data))
            pil_image.save(image_path, "WEBP", lossless=False, quality=80)
        elif image_format.lower() == "jpg":
            pix.save(image_path, jpg_quality=95)
        else:
            pix.save(image_path)

        image_paths.append(f"img/{image_name}")

    doc.close()

    # Создаём HTML
    html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body { margin: 0; padding: 0; }
  img { display: block; margin: 0 auto 5px auto; width: 100%; }
  @media (min-width: 768px) { img { width: 900px; } }
</style>
</head>
<body>
"""
    for img in image_paths:
        html_content += f'<img src="{img}" alt="Page">\n'
    html_content += "</body></html>"

    html_path = os.path.join(output_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Собираем в ZIP
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Добавляем HTML
        zipf.write(html_path, "index.html")
        # Добавляем изображения
        for img_path in image_paths:
            abs_path = os.path.join(output_dir, img_path)
            zipf.write(abs_path, img_path)
