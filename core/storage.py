from django.core.files.storage import FileSystemStorage
from django.conf import settings

protected_storage = FileSystemStorage(location=settings.PROTECTED_MEDIA_ROOT)