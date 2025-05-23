from django.contrib import admin
from .models import CachedBooks

@admin.register(CachedBooks)
class CachedBooksAdmin(admin.ModelAdmin):
    list_display = ('id', 'book_data_preview', 'content_preview', 'substance_preview')
    search_fields = ('content', 'substance')
    list_per_page = 20

    def book_data_preview(self, obj):
        return str(obj.book_data)[:50] + '...' if obj.book_data else ''
    book_data_preview.short_description = 'Book Data'

    def content_preview(self, obj):
        return str(obj.content)[:50] + '...' if obj.content else ''
    content_preview.short_description = 'Content'

    def substance_preview(self, obj):
        return str(obj.substance)[:50] + '...' if obj.substance else ''
    substance_preview.short_description = 'Substance'

    def dasda_dadwa(self, obj):
        return str(obj.covers)[:50] + '...' if obj.covers else ''
    substance_preview.short_description = 'Covers'