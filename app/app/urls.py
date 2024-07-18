"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

admin.site.site_header = "Canvas Wizards Administration"
admin.site.site_title = "Canvas Wizards Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('front.urls')),
    path('choices/', include('choices.urls')),
    path('report/', include('report.urls')),
    path('adjustments/', include('adjustments.urls')),
    path('panorama/', include('panorama.urls')),
    path('projects/', include('projects.urls')),
    path('ilo/', include('ilo.urls')),
    path('expertise/', include('ilo.urls')),
    path('captionsearch/', include('captionsearch.urls')),
    path('tools/', include('tools.urls')),
    path('dataspell/', include('sample.urls')),
    path('showcase/', include('presentations.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
