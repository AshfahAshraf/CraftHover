
from django.contrib import admin
from django.urls import path,include

#my account profile 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include('user.urls')),
    path('admin-panel/', include('admin_app.urls')),

    
]

#for serving media file for my account

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
