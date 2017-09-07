from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='employee_default'),
    url(r'^info$', views.info, name='employee_info'),
    url(r'^all$', views.all, name='all_employee'),
    url(r'^upload$', views.upload_file, name='upload_file'),
    url(r'^home$', views.home, name='employee_home'),
    url(r'^document_download$', views.document_download, name='document_download'),
    url(r'^backup', views.backup, name='backup'),
    url(r'^report', views.report, name='report'),
]
