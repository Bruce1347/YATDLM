"""yatdlm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.conf import settings
from todo import views as todo_views

urlpatterns = [
    # Django admin urls (TODO: enable/disable it through configuration variables)
    path("admin/", admin.site.urls),
    # Urls linked to the todo app
    path("todo/", include("todo.urls")),
    # Redirection from <url>/ to <url>/login
    path(r"", RedirectView.as_view(url="/login")),
    # Login page
    path("login", todo_views.display_login),
    # Login request
    path("login/auth", todo_views.user_login),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path(r"__debug__/", include(debug_toolbar.urls)),
    ]
