# corpus/admin.py
from django.contrib import admin
from .models import Text, Metadata, UnknownWord, UnknownWordBatch, VersionedText


class TextAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date', 'status')


class UnknownWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'text')
    search_fields = ["word"]


class VersionedTextAdmin(admin.ModelAdmin):
    list_display = ('text', 'version_number', 'created_at', 'updated_at')


admin.site.register(Text, TextAdmin)
admin.site.register(Metadata)
admin.site.register(UnknownWord, UnknownWordAdmin)
admin.site.register(UnknownWordBatch)
admin.site.register(VersionedText, VersionedTextAdmin)
