from django.contrib import admin
from django.urls import path
from rest_framework.documentation import include_docs_urls

from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('records', views.RecordCreate.as_view()),
    path('bills/<subscriber>', views.BillList.as_view()),
    path('', include_docs_urls(title='Phone Manager API')),
]
