from django.db import models

class Upload_Media(models.Model):
    upload_media = models.FileField(upload_to='Uploaded_Media/', null=True, blank=True)

    def __str__(self):
        return str(self.upload_media)
