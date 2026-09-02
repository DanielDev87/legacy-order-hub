from django.urls import path

from apps.catalog.api.views import CreateProductView

urlpatterns = [
    path("products", CreateProductView.as_view(), name="create_product"),
]
