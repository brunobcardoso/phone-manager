from django.contrib import admin

from core.models import Call, Record, Bill


class CallAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'destination')


class RecordAdmin(admin.ModelAdmin):
    list_display = ('call', 'type', 'timestamp')


class BillAdmin(admin.ModelAdmin):
    list_display = ('call', 'price', 'start', 'end')


admin.site.register(Call, CallAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(Bill, BillAdmin)
