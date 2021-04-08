from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """ base reicpe attrubutes viewset """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """ return objects for current authenticated user"""
        return self.queryset.filter(user = self.request.user)

    def perform_create(self, serializer):
        """create new object"""
        serializer.save(user = self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """ mange tags in database """
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """ manage ingredients in database """

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """ manage recipes in the database """
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """ retrive recipes for authenticated user only"""
        return self.queryset.filter(user = self.request.user)

    def get_serializer_class(self):
        """ return appropriate serializer class """

        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """ create recipe object"""
        serializer.save(user = self.request.user)