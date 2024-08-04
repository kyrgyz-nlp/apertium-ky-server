from django.db import models


class Text(models.Model):
    STATUS_CHOICES = [
        ('Uploaded', 'Uploaded'),
        ('Processing', 'Processing'),
        ('Cleaned', 'Cleaned'),
        ('Annotated', 'Annotated'),
        ('Completed', 'Completed'),
        ('Error', 'Error'),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    date = models.DateField()
    source = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Uploaded')


class VersionedText(models.Model):
    text = models.ForeignKey(Text, on_delete=models.CASCADE)
    version_number = models.PositiveIntegerField(default=1)
    updated_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Metadata(models.Model):
    text = models.ForeignKey(Text, on_delete=models.CASCADE)
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=255)


class UnknownWord(models.Model):
    word = models.CharField(max_length=255)
    text = models.ForeignKey(Text, on_delete=models.CASCADE)
    context = models.TextField()
    is_typo = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    correct_form = models.CharField(max_length=255, null=True, blank=True)
    positions = models.JSONField()


class UnknownWordBatch(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Checked', 'Checked'),
        ('UpdatingApertium', 'Updating Apertium'),
        ('RebuildingApertium', 'Rebuilding Apertium'),
        ('Rechecking', 'Rechecking'),
        ('Completed', 'Completed'),
    ]

    text = models.ForeignKey(Text, on_delete=models.CASCADE)
    words = models.ManyToManyField(UnknownWord)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
