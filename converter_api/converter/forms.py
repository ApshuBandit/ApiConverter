from django import forms

class UploadForm(forms.Form):
    file = forms.FileField(label="Выберите PDF")
    format = forms.ChoiceField(
        choices=[
            ("jpg", "JPG"),
            ("png", "PNG"),
            ("webp", "WEBP"),
        ],
        initial="webp"
    )
