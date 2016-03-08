from django.conf.urls.defaults import patterns

import views
import app_settings

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns(
    '',
    (r'^json/?', views.packages),
    (r'^(?P<package_name>[^\/]+)/json/?', views.package_releases),
    (r'^latest/(?P<package_name>[^\/]+)(/(?P<app_major>\d+)'
     r'(\.?P<app_minor>\d+)?(\.?P<app_micro>\d+)?)?/?',
     views.redirect_to_latest),
    (r'^data/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': app_settings.DATA_DIR, 'show_indexes': True}),
)
