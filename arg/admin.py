from django.contrib import admin
from django.utils.html import format_html
from .models import LorePage, PageScan, ContactSubmission


class PageScanInline(admin.TabularInline):
    model = PageScan
    extra = 0
    readonly_fields = ('ip_address', 'user_agent', 'session_key', 'timestamp', 'is_first_visit')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(LorePage)
class LorePageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_secret', 'scan_count', 'created_at')
    list_filter = ('is_secret',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PageScanInline]

    def scan_count(self, obj):
        return obj.scans.count()
    scan_count.short_description = 'Сканов'


@admin.register(PageScan)
class PageScanAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'page_link', 'ip_address', 'is_first_visit', 'short_ua')
    list_filter = ('page', 'is_first_visit')
    readonly_fields = ('page', 'ip_address', 'user_agent', 'session_key', 'timestamp', 'is_first_visit')
    date_hierarchy = 'timestamp'

    def page_link(self, obj):
        return format_html('<a href="/archive/{}">{}</a>', obj.page.slug, obj.page.title)
    page_link.short_description = 'Страница'

    def short_ua(self, obj):
        ua = obj.user_agent
        return (ua[:60] + '...') if len(ua) > 60 else ua
    short_ua.short_description = 'User-Agent'

    def has_add_permission(self, request):
        return False


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'ip_address', 'short_subject', 'agent_id', 'triggered_special', 'triggered_unlock')
    list_filter = ('triggered_special', 'triggered_unlock')
    readonly_fields = ('subject', 'message', 'agent_id', 'ip_address', 'session_key',
                       'timestamp', 'triggered_special', 'triggered_unlock')
    date_hierarchy = 'timestamp'

    def short_subject(self, obj):
        s = obj.subject
        return (s[:50] + '...') if len(s) > 50 else s
    short_subject.short_description = 'Тема'

    def has_add_permission(self, request):
        return False
