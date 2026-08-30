from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from accounts import views

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "",
        include("accounts.urls"),
    ),

    path(
        "courses/",
        include("courses.urls"),
    ),

    path(
        "notifications/",
        include("notifications.urls"),
    ),

    path(
        "chat/",
        include("chat.urls"),
    ),

    path(
        "api/",
        include("api.urls"),
    ),

    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),

    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema"
        ),
        name="swagger-ui",
    ),

    path(
        "api/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema"
        ),
        name="redoc",
    ),
    
    path(
        "api-documentation/",
        views.api_docs,
        name="api_docs",
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )