from django.contrib.postgres.fields import JSONField
from django.db import models

# Create your models here.


class Tag_Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)

    def ___str___(self):
        return self.name


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    category = models.ForeignKey(Tag_Category, on_delete=models.CASCADE)

    def ___str___(self):
        return self.name


class Ingredient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)

    def ___str___(self):
        return self.name


class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    creator = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    image = models.FileField(upload_to='recipe-images/')
    thumbnail = models.FileField(upload_to='recipe-thumbs/')
    amount_persons = models.PositiveSmallIntegerField()
    cook_time_minutes = models.PositiveSmallIntegerField()
    instructions = models.CharField(max_length=4096)
    is_deleted = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag)

    def ___str___(self):
        return self.name


class IngredientSet(models.Model):
    id = models.AutoField(primary_key=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    name = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField()
    unit = models.CharField(max_length=16)

    def ___str___(self):
        return self.name


class Recipe_Book(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    recipe = models.ManyToManyField(Recipe)

    def ___str___(self):
        return self.id