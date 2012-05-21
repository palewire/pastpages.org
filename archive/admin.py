from django.contrib import admin
from archive.models import Site, Update, Screenshot, Champion


class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "status", "on_the_homepage")
    list_filter = ("status",)
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ('status', 'on_the_homepage')

admin.site.register(Site, SiteAdmin)


class UpdateAdmin(admin.ModelAdmin):
    list_display = ('start',)
    date_hierarchy = 'start'

admin.site.register(Update, UpdateAdmin)


class ScreenshotAdmin(admin.ModelAdmin):
    list_display = ("site", "update",)

admin.site.register(Screenshot, ScreenshotAdmin)


class ChampionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Champion, ChampionAdmin)
