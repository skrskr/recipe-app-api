from rest_framework import generics

from users.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """ create new user in the system """
    serializer_class = UserSerializer
    

