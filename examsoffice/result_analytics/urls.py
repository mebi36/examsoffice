from django.urls.conf import path

from result_analytics import views


app_name = "result_analytics"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("collated_results/", views.export_pivot_csv, name="collated_results"),
    path("api/result_analytics/preview_excel/", views.preview_excel, name="preview_excel"),
    path("api/result_analytics/upload_excel_file/", views.upload_excel_file, name="upload_excel_file"),
    path("api/result_analytics/cache_result_data/", views.cache_result_data),
    path("api/result_analytics/list_results/", views.list_results),
    path("api/result_analytics/get/<int:result_id>/", views.get_result),
    path("api/result_analytics/delete/<int:result_id>/", views.delete_result),
    path("api/result_analytics/clear_results/", views.clear_results),
]
