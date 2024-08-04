# corpus/admin.py
from django.contrib import admin
from .models import Text, Metadata, UnknownWord, UnknownWordBatch, VersionedText


class TextAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date', 'status')


class UnknownWordBatchAdmin(admin.ModelAdmin):
    list_display = ('text', 'status')
    filter_horizontal = ('words',)


class VersionedTextAdmin(admin.ModelAdmin):
    list_display = ('text', 'version_number', 'created_at', 'updated_at')


admin.site.register(Text, TextAdmin)
admin.site.register(Metadata)
admin.site.register(UnknownWord)
admin.site.register(UnknownWordBatch, UnknownWordBatchAdmin)
admin.site.register(VersionedText, VersionedTextAdmin)
