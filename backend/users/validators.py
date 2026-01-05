import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _



def validate_file_extension(value):
    extension = os.path.splitext(value.name)[1]
    valid_extensions = [
        # Images
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff', '.tif',
        # Documents
        '.pdf', '.doc', '.docx', '.txt', '.rtf',
        # Spreadsheets
        '.xls', '.xlsx', '.csv',
        # Presentations
        '.ppt', '.pptx',
        # Archives
        '.zip', '.rar', '.7z'
    ]
    
    if not extension.lower() in valid_extensions:
        raise ValidationError(
            _('Unsupported file extension. Allowed extensions: %(valid_extensions)s'),
            params={'valid_extensions': ', '.join(valid_extensions)}
        )

def validate_file_size(value):
    extension = os.path.splitext(value.name)[1]
    valid_extensions = ["pdf", ".jpeg", ".png"]
    if not extension.lower() in valid_extensions:
        raise ValidationError("Unsupported file extension. Only JPG, JPEG, PNG allowed.")