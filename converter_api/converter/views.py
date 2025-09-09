import io
import zipfile
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from PIL import Image
import fitz  # PyMuPDF

from .serializers import FileConvertSerializer


class ImageConvertAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = FileConvertSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        files = serializer.validated_data["files"]
        target_format = serializer.validated_data["format"]

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            image_paths: list[str] = []

            for idx, file in enumerate(files, start=1):
                filename = file.name.lower()

                if filename.endswith(".pdf"):
                    pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
                    for page_num, page in enumerate(pdf_doc, start=1):
                        pix = page.get_pixmap()
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                        img_name = f"images/pdf_{idx}_page{page_num}.{target_format}"
                        image_paths.append(img_name)

                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format=target_format.upper())
                        zip_file.writestr(img_name, img_bytes.getvalue())
                else:
                    img = Image.open(file).convert("RGB")
                    img_name = f"images/img_{idx}.{target_format}"
                    image_paths.append(img_name)

                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format=target_format.upper())
                    zip_file.writestr(img_name, img_bytes.getvalue())

            # создаём index.html
            html_content = "<html><body><h1>Converted Files</h1>"
            for path in image_paths:
                html_content += f'<div><img src="{path}" style="max-width:400px;"></div>'
            html_content += "</body></html>"

            zip_file.writestr("index.html", html_content)

        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="converted.zip"'
        return response
