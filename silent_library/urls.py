from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Root path for the app, using a unique namespace
    path('', include('my_app.urls', namespace='root_my_app')),  

    # Admin path for the Django admin
    path('admin/', admin.site.urls), 

    # Path for 'my_app/' with a unique namespace
    path('my_app/', include('my_app.urls', namespace='my_app')),  

    # Path for 'userprofile/' with a unique namespace
    path('userprofile/', include('my_app.urls', namespace='userprofile_my_app')),  
]

# Serve media files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
