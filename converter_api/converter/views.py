import os
import tempfile
from django.http import FileResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import ConvertSerializer
from .forms import UploadForm
from .utils import pdf_to_images_and_html


# ===============================
# 1. APIView для DRF
# ===============================
class ImageConvertAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = ConvertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pdf_file = serializer.validated_data['files']
        fmt = serializer.validated_data['format']

        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "converted.zip")
            pdf_to_images_and_html(pdf_file, tmpdir, fmt, zip_path)

            return FileResponse(
                open(zip_path, "rb"),
                as_attachment=True,
                filename="converted.zip"
            )


# ===============================
# 2. HTML-форма для сайта
# ===============================
def upload_view(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['file']
            fmt = form.cleaned_data['format']

            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = os.path.join(tmpdir, "converted.zip")
                pdf_to_images_and_html(pdf_file, tmpdir, fmt, zip_path)

                return FileResponse(
                    open(zip_path, "rb"),
                    as_attachment=True,
                    filename="converted.zip"
                )
    else:
        form = UploadForm()

    return render(request, "upload.html", {"form": form})
