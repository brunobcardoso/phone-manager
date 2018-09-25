from django.contrib import admin

from core.models import Call, Record


class CallAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'destination')


class RecordAdmin(admin.ModelAdmin):
    list_display = ('call', 'type', 'timestamp')


admin.site.register(Call, CallAdmin)
admin.site.register(Record, RecordAdmin)
