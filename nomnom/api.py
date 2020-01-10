from django.shortcuts import render
from rest_framework import viewsets
from .models import Tag_Category
from .serializers import Tag_Category_Serializer


# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse


def index(request):
    return HttpResponse("Hello, world. You're at the index.")


def get_all_tag_categories(request):
    if request.method == 'GET':
        tagC = Tag_Category.objects.all()
        serializer = Tag_Category_Serializer(tagC, many=True, )
        return JsonResponse(serializer.data, safe=False)