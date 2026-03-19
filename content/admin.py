from django.contrib import admin

from content.models import Fragment


@admin.register(Fragment)
class FragmentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description")
    list_filter = ("is_active", "title")
