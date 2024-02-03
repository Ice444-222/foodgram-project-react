from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           FilterSet,
                                           ModelMultipleChoiceFilter)

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """
    Фильтр унаследованный от фильтрсета для ингредиентов, который позволяет
    искать ингредиент по имени.
    """

    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """
    Фильтр унаследованный от фильтрсета для рецептов, который позволяет
    искать рецепты по автору, тегам и boolean значениям аннотированного
    queryset'а рецептов.
    """

    author = CharFilter(field_name='author__id', lookup_expr='iexact')
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = BooleanFilter(field_name='is_favorited')
    is_in_shopping_cart = BooleanFilter(field_name='is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = (
            'author', 'tags__slug', 'is_favorited', 'is_in_shopping_cart'
        )

    def filter_tags(self, queryset, name, value):
        return queryset.filter(tags__slug__in=value)
