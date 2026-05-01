from django.urls import path
from . import views

app_name = 'arg'

urlpatterns = [
    path('',                    views.index,       name='index'),
    path('archive/',            views.archive,     name='archive'),
    path('archive/<str:case_id>/', views.case_detail, name='case_detail'),
    path('cases/',              views.cases,       name='cases'),
    path('protocols/',          views.protocols,   name='protocols'),
    path('contact/',            views.contact,     name='contact'),
    path('about/',              views.about,       name='about'),
    path('observer/',           views.observer,    name='observer'),
    path('shadow/14-04/',       views.shadow,      name='shadow'),
    path('arg-log/',            views.scan_log,    name='scan_log'),
]
