from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UpdateMembershipFeeAPISerializer

# Create your views here.


class UpdateMembershipFeeAPI(APIView):
    """
    API for superuser to update the membership fee
    """
    def post(self, request):
        serializer = UpdateMembershipFeeAPISerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        message = "Membership fee updated successfully"
        return Response([{"status": message}], status=status.HTTP_201_CREATED)
