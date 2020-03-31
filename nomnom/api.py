from rest_framework.authtoken import views
from rest_framework.views import APIView
from rest_framework import status
from .models import Tag_Category, Tag, Ingredient, Recipe, IngredientSet
from .serializers import Tag_Category_Serializer, IngredientSet_Serializer, Ingredient_Serializer, Tag_Serializer, Recipe_Serializer_Short, Recipe_Serializer
from .api_lib.searchers import IngredientSearcher, TagSearcher, RecipeSearcher, IngredientSetSearcher

# Authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from oauth2_provider.views.generic import ProtectedResourceView

# Response Libraries
from django.http import HttpResponse
from django.http import JsonResponse


class Add_Edit_Recipe(APIView):
    def post(self, request):
        try:
            # create basic recipe model
            recipe_data = request.data['recipe']
            user = request.headers['Authorization']
            if (recipe_data['id'] is None):
                recipe = Recipe(creator=request.user, name=recipe_data['name'], amount_persons=recipe_data['amount_persons'],
                                cook_time_minutes=recipe_data['cook_time_minutes'],
                                instructions=recipe_data['instructions'], is_deleted=False)

            else:
                recipe = Recipe(id=recipe_data['id'], creator=request.user, name=recipe_data['name'], amount_persons=recipe_data['amount_persons'],
                                cook_time_minutes=recipe_data['cook_time_minutes'],
                                instructions=recipe_data['instructions'], is_deleted=False)

            recipe.save()

            # auto-subscribe creator

            recipe.subscribed_by.add(request.user)

            # create tags and add to existing recipe
            for tag_data in recipe_data['tags']:
                try:
                    tag = Tag.objects.filter(id=tag_data['uniqueId'])
                    recipe.tags.add(tag[0])

                except RuntimeError as error:
                    return HttpResponse(error, status=status.HTTP_400_BAD_REQUEST)
                recipe.save()
            # create ingredientsets and connect to recipe
            for ingredient_data in recipe_data['ingredients']:
                try:
                    ingredient = Ingredient.objects.filter(
                        id=ingredient_data['id'])
                except RuntimeError as error:
                    return HttpResponse(error, status=status.HTTP_400_BAD_REQUEST)
                ingredientSet = IngredientSet(
                    recipe=recipe, ingredient=ingredient[0], amount=ingredient_data['amount'], unit=ingredient_data['unit'])
                ingredientSet.save()

            # return newly given recipe id for client access it
            response = {'new_recipe_id': recipe.id}
            return JsonResponse(response, status=status.HTTP_200_OK)

        except RuntimeError as error:
            return HttpResponse(error, status=status.HTTP_400_BAD_REQUEST)


class Ingredients_List(APIView):
    def get(self, request):
        """Returns a JSON of all Existing Ingredients"""
        ingredients = Ingredient.objects.all()
        serializer = Ingredient_Serializer(ingredients, many=True)
        return JsonResponse(serializer.data, safe=False)


class Recipe_List(APIView):
    def get(self, request):
        ''' Returns all Recipe names '''
        recipes = Recipe.objects.all()
        serializer = Recipe_Serializer_Short(recipes, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


class Ingredients_Search(APIView):

    def post(self, request):
        """Returns a JSON of Recipes which contain the ingredients,
        provided by the request

        @param: list<String> request.data
        """
        print(request.user)
        try:
            searcher = IngredientSearcher(
                request.data['ingredients'], request.data['search-type'])
            if (request.data['search-type'] == "AND"):
                recipes = searcher.and_search()
            else:
                recipes = searcher.or_search()
            serializer = Recipe_Serializer_Short(recipes, many=True)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        except RuntimeError as error:
            return HttpResponse(error, status=status.HTTP_400_BAD_REQUEST)


class Tag_Search(APIView):
    def post(self, request):
        try:
            searcher = TagSearcher(request.data['data'])
            recipeData = searcher.search()
            return JsonResponse(recipeData, status=status.HTTP_200_OK)
        except RuntimeError as error:
            return HttpResponse(error, status=status.HTTP_400_BAD_REQUEST)


class Recipe_Search(APIView):
    def post(self, request):
        try:
            searcher = RecipeSearcher(request.data['id'])
            recipe_data = searcher.search()
            serializer = Recipe_Serializer_Short(recipe_data)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        except RuntimeError as error:
            return HttpResponse(error, status=status.HTTP_400_BAD_REQUEST)


class Recipe_Details(APIView):
    def post(self, request):
        requestedID = request.data['id']
        try:
            searcher = RecipeSearcher(requestedID)
            recipe_data = searcher.search()
            recipe_serializer = Recipe_Serializer(recipe_data)
            return JsonResponse(recipe_serializer.data, status=status.HTTP_200_OK)
        except RuntimeError as error:
            return HttpResponse(error, status=status.HTTP_400_BAD_REQUEST)


class Tag_Tag_Category_List(APIView):
    def get(self, request):
        tagC = Tag_Category.objects.all()
        tags = Tag.objects.all()
        tagC_serializer = Tag_Category_Serializer(tagC, many=True)
        tags_serializer = Tag_Serializer(tags, many=True)

        tagInformation = {'tags': tags_serializer.data,
                          'tagCategories': tagC_serializer.data}

        return JsonResponse(tagInformation, status=status.HTTP_200_OK)


class Tag_Category_List(APIView):
    def get(self, request, format=None):
        tag_categories = Tag_Category.objects.all()
        serializer = Tag_Category_Serializer(tag_categories, many=True)
        return JsonResponse(serializer.data)


def index(request):
    return HttpResponse("Hello, world. You're at the index.")
