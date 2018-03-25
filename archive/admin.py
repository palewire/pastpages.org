from django.contrib import admin
from archive.models import Site, Update, Screenshot, Champion, ScreenshotLog, Memento


class SiteAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "status",
        "has_html_screenshots",
        "on_the_homepage",
        "has_internetarchive_mementos",
        'has_archiveis_mementos',
        "has_webcitation_mementos"
    )
    list_filter = (
        "status",
        'has_html_screenshots',
        'has_internetarchive_mementos',
        'has_archiveis_mementos',
        'has_webcitation_mementos',
        'on_the_homepage',
    )
    prepopulated_fields = {"slug": ("name",)}


class UpdateAdmin(admin.ModelAdmin):
    list_display = ('start',)
    date_hierarchy = 'start'


class ScreenshotAdmin(admin.ModelAdmin):
    list_display = ("site", "update",)
    readonly_fields = (
        'site',
        'update',
        'timestamp',
        'internetarchive_id',
        #'ia_url',
        'internetarchive_crop_url',
        'internetarchive_image_url',
        'has_image',
        'has_crop',
        'has_html',
        'image',
        'crop',
        'html',
    )


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


class MementoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "site",
        "update",
        "archive",
    )
    list_filter = ("archive",)
    date_hierarchy = "timestamp"
    search_fields = (
        "site__name",
        "archive"
    )
    readonly_fields = (
        "site",
        "update",
        "timestamp",
        "archive",
        "url"
    )


admin.site.register(Site, SiteAdmin)
admin.site.register(Update, UpdateAdmin)
admin.site.register(Screenshot, ScreenshotAdmin)
admin.site.register(Champion, ChampionAdmin)
admin.site.register(ScreenshotLog, ScreenshotLogAdmin)
admin.site.register(Memento, MementoAdmin)
