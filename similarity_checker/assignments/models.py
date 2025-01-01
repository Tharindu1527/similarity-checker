from django.db import models
from django.core.validators import FileExtensionValidator

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(
        upload_to='assignments/',
        validators=[FileExtensionValidator(allowed_extensions=['txt', 'doc', 'docx', 'pdf'])]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title