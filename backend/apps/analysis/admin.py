from django.contrib import admin
from .models import AnalysisReport


@admin.register(AnalysisReport)
class AnalysisReportAdmin(admin.ModelAdmin):
    list_display = ["report_type", "generated_at"]
    list_filter = ["report_type"]
    date_hierarchy = "generated_at"

    def data_preview(self, obj):
        import json
        raw = json.dumps(obj.data, ensure_ascii=False, indent=2)
        return f"<pre>{raw[:300]}...</pre>" if len(raw) > 300 else f"<pre>{raw}</pre>"

    data_preview.short_description = "数据预览"
    data_preview.allow_tags = True

    readonly_fields = ["generated_at", "data_preview"]
    fields = ["report_type", "generated_at", "data", "data_preview"]
