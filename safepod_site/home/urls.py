from django.conf.urls import patterns, url

from .views import HomeView

urlpatterns = [
                       url(r'^$', HomeView.as_view(), name='index'),
            ]