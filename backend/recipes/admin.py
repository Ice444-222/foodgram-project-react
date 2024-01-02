from django.contrib import admin

from .models import (Tag,
                     Recipe,
                     Ingredient,
                     RecipesIngredients)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    list_filter = ('author', 'name', 'tags__name',)
    
    def favorites_count(self, obj):
        return obj.favorites.count()

    favorites_count.short_description = 'Добовлено в избранное количество раз'

class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


admin.site.register(Tag)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipesIngredients)