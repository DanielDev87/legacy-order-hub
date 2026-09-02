from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.api.serializers import CreateProductRequestSerializer
from apps.catalog.application.services import CatalogService
from apps.catalog.infrastructure.repositories import DjangoProductRepository
from common.api.permissions import IsAdminRole


class CreateProductView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request):
        serializer = CreateProductRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        service = CatalogService(product_repository=DjangoProductRepository())
        try:
            product_id = service.create_product(**serializer.validated_data)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Producto creado con éxito", "product_id": product_id},
            status=status.HTTP_201_CREATED,
        )
