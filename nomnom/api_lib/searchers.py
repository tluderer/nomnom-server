""" This class handles all searching operations """

from nomnom.models import IngredientSet, Recipe, Ingredient
from collections import Counter
from nomnom.serializers import Recipe_Serializer_Short, IngredientSet_Serializer, Ingredient_Serializer, Recipe_Serializer


class IngredientSetSearcher:
    def __init__(self, recipe_id: int):
        self.searched_recipe_id = recipe_id

    def search(self):
        searched_recipe = Recipe.objects.filter(
            id=self.searched_recipe_id, is_deleted=False)
        found_ingredient_sets = IngredientSet.objects.filter(
            recipe__in=searched_recipe).select_related('ingredient')

        ingredientset_list = []

        for ingredientset in found_ingredient_sets:
            serializer = IngredientSet_Serializer(ingredientset)
            ingredientset_list.append(serializer.data)

        for ingredientset in ingredientset_list:
            pass

        if found_ingredient_sets:
            return ingredientset_list
        else:
            raise RuntimeError()


class RecipeSearcher:
    def __init__(self, recipe_id: int, requester: str):
        self.searched_recipe_id = recipe_id
        self.requester = requester

    def search(self):
        found_recipe = Recipe.objects.filter(
            id=self.searched_recipe_id, is_deleted=False)
        if found_recipe:  # read: if found recipe not empty
            if found_recipe[0].creator == self.requester:
                is_owner = True
            else:
                is_owner = False
            print(found_recipe[0])
            is_subscriber = False
            for username in found_recipe[0].subscribed_by.all():
                if username == self.requester:
                    is_subscriber = True

            return {'recipe': found_recipe[0], 'isOwner': is_owner, 'isSubscribed': is_subscriber}
        else:
            raise RuntimeError()


class TagSearcher:
    def __init__(self, search_content: list, search_range: str, requester: str):
        self.searched_tags = search_content
        self.search_range = search_range
        self.requester = requester

    # TODO: Filter for subscribed
    def search(self):
        taglist_length = len(self.searched_tags)
        found_tags = []

        for tag in self.searched_tags:
            # print(tag)
            unique_id = int(tag['uniqueId'])
            # print(uniqueId)
            found_tags.append(unique_id)

        all_found_recipes_or = []
        for tags_id in found_tags:
            all_found_recipes_or += Recipe.objects.filter(
                tags__id=tags_id, is_deleted=False)

        counted_recipes_or = Counter(all_found_recipes_or)
        reduced_found_recipes_or = []

        if self.search_range == "subscribed":
            for unique_recipe_or in counted_recipes_or:
                for subscriber in unique_recipe_or.subscribed_by.all():
                    if self.requester == subscriber:
                        reduced_found_recipes_or.append(unique_recipe_or)
        else:
            for unique_recipe_or in counted_recipes_or:
                reduced_found_recipes_or.append(unique_recipe_or)

        all_found_recipes_and = []
        for tagsId in found_tags:
            all_found_recipes_and += Recipe.objects.filter(
                tags__id=tagsId, is_deleted=False)

        c = Counter(all_found_recipes_and)
        reduced_found_recipes_and = []
        taglist_length_equals = Counter(
            recipe for recipe in c.elements() if c[recipe] == taglist_length)

        if self.search_range == "subscribed":
            for found_recipe in taglist_length_equals:
                for subscriber in found_recipe.subscribed_by.all():
                    if self.requester == subscriber:
                        reduced_found_recipes_and.append(found_recipe)
        else:
            for found_recipe in taglist_length_equals:
                reduced_found_recipes_and.append(found_recipe)

        and_serializer = Recipe_Serializer_Short(
            reduced_found_recipes_and, many=True)
        or_serializer = Recipe_Serializer_Short(
            reduced_found_recipes_or, many=True)

        response = {'all_tags': and_serializer.data,
                    'one_or_more_tags': or_serializer.data}

        return(response)


class IngredientSearcher:
    def __init__(self, search_content: list, search_type: str, search_range: str, requester: str):
        self.searched_ingredients = search_content
        self.operator = search_type
        self.search_range = search_range
        self.requester = requester

    # TODO: Filter for subscribed type

    def or_search(self):
        intro = "Searching: \"" + \
            ', '.join(self.searched_ingredients) + \
            "\" with operator: " + self.operator + \
            "\" with range: " + self.search_range

        # The following code creates a List ingredient_sets_queries which contains all ingredient_sets
        # containing the searched Ingredients
        ingredient_sets = []

        print(intro)
        for ingredient_word in self.searched_ingredients:

            found_ingredient_set = IngredientSet.objects.filter(
                ingredient__name=ingredient_word)  # field lookup
            ingredient_sets += found_ingredient_set

        # extract and save the found recipes

        #TODO: Filter deleted Recipes!
        found_recipes = []
        if self.search_range == "subscribed":
            for ingredient_set in ingredient_sets:
                for subscriber in ingredient_set.recipe.subscribed_by.all():
                    if self.requester == subscriber:
                        found_recipes.append(ingredient_set.recipe)
        else:
            for ingredient_set in ingredient_sets:
                found_recipes.append(ingredient_set.recipe)

        # reduce list to unique Recipes
        countedRecipes = Counter(found_recipes)
        uniqueRecipeList = []
        for uniqueRecipe in countedRecipes:
            uniqueRecipeList.append(uniqueRecipe)

        return uniqueRecipeList

    def and_search(self):
        intro = "Searching: \"" + \
            ', '.join(self.searched_ingredients) + \
            "\" with operator: " + self.operator + \
            "\" with range: " + self.search_range

        search_word_count = len(self.searched_ingredients)

        # This code creates a List ingredient_sets_queries which contains all ingredient_sets
        # containing the searched Ingredients
        print(intro)

        ingredient_sets_queries = []
        for ingredient_word in self.searched_ingredients:
            found_ingredient_set = IngredientSet.objects.filter(
                ingredient__name=ingredient_word)  # field lookup
            ingredient_sets_queries.append(found_ingredient_set)

        ##
        # The following code creates a List recipe_list, which contains all Recipes
        # associated with the found ingredient_sets.
        # This means, the found recipes contain the searched Ingredients

        recipe_list = []
        #TODO: Filter deleted Recipes!

        # search every search query separately
        for ingredient_sets_query in ingredient_sets_queries:
            current_query = []
            # get the assigned recipe to the current ingredient_set
            for ingredient_set in ingredient_sets_query:
                current_query.append(ingredient_set.recipe)

            # one recipe could theoretically contain multiple found ingredient sets
            # the following code block reduces the found recipes to unique values
            counted_query_recipes = Counter(current_query)
            unique_recipe_list = []
            for unique_recipe in counted_query_recipes:
                unique_recipe_list.append(unique_recipe)

            # add the unique recipes to recipe_list
            recipe_list += (unique_recipe_list)

        # now that all recipes are added, all recipes are extracted, which appear
        # n times in the List
        # where n is the search_word_count
        c = Counter(recipe_list)
        search_word_equals = Counter(
            recipe for recipe in c.elements() if c[recipe] == search_word_count)

        # make a list out of it
        found_recipes = []
        if self.search_range == "subscribed":
            for found_recipe in search_word_equals:
                for subscriber in found_recipe.subscribed_by.all():
                    if self.requester == subscriber:
                        found_recipes.append(found_recipe)

        else:
            for found_recipe in search_word_equals:
                found_recipes.append(found_recipe)

        return found_recipes
