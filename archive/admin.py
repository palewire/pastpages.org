from django.contrib import admin
from archive.models import Site, Update, Screenshot, Champion, ScreenshotLog


class SiteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "has_html_screenshots",
        "on_the_homepage"
    )
    list_filter = ("status",)
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ('status', 'has_html_screenshots', 'on_the_homepage')


class UpdateAdmin(admin.ModelAdmin):
    list_display = ('start',)
    date_hierarchy = 'start'


class ScreenshotAdmin(admin.ModelAdmin):
    list_display = ("site", "update",)
    readonly_fields = ('site', 'update', 'timestamp')


class ChampionAdmin(admin.ModelAdmin):
    pass


class ScreenshotLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "update",
        "site",
        "message_type",
        "message"
    )
    list_filter = ("message_type", "site")
    readonly_fields = (
        "update",
        "site",
        "screenshot",
        "message_type",
        "message"
    )


admin.site.register(Site, SiteAdmin)
admin.site.register(Update, UpdateAdmin)
admin.site.register(Screenshot, ScreenshotAdmin)
admin.site.register(Champion, ChampionAdmin)
admin.site.register(ScreenshotLog, ScreenshotLogAdmin)