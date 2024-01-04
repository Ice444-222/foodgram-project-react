from django_filters.rest_framework import CharFilter, FilterSet, ModelChoiceFilter, BooleanFilter, LookupChoiceFilter
from django.db.models import F, Exists, OuterRef
from recipes.models import Ingredient, Recipe






class IngredientFilter(FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    author = CharFilter(field_name='author__id', lookup_expr='iexact')
    tags = LookupChoiceFilter(
        field_name='tags__slug',
        lookup_expr='iexact',
        conjoined=True
    )
    is_favorited = BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author','tags__slug', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            user=self.request.user
            if user.is_authenticated:
                return user.favorites.all()
        return queryset
    
    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            user=self.request.user
            if user.is_authenticated:
                return user.groceries_list.all()
        return queryset