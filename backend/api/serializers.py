from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import BadRequest
from rest_framework import status
from rest_framework.response import Response
import base64
from django.core.files.base import ContentFile
from drf_writable_nested import WritableNestedModelSerializer
from django.db.models import F

from recipes.models import Tag, Recipe, RecipesIngredients, Ingredient, RecipesIngredients

User = get_user_model()

class UserBasicSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
        ]
        extra_kwargs = {
            'is_subscribed': {'read_only': True},
        }

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.subscriptions.filter(subscription=obj).exists()
        else:
            return False


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            ]
        extra_kwargs = {
            'password': {'write_only': True},
        }


class UserNewPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['current_password', 'new_password']

    def validate(self, attrs):
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        user = self.context['request'].user
        if current_password!=user.password:
            raise serializers.ValidationError('Incorrect current password.')
        user.password = new_password
        user.save(update_fields=['password'])

        return attrs

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

    def to_representation(self, file):
        return '/media/' + super().to_representation(file)


class CustomTokenObtainPairSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    email = serializers.CharField(write_only=True)

    class Meta:
        fields = ['password', 'email']

    def validate(self, attrs):
        password = attrs.get("password")
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise BadRequest("Failed")

        if user.password != password:
            raise ValidationError
        attrs["user"] = user
        return attrs

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ["id", "name", "color", "slug"]

class RecipesIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(read_only=True)
    measurement_unit = serializers.CharField(read_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipesIngredients
        fields = ("id", "name", "measurement_unit", "amount")

class RecipesSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients =  serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ["id", "tags", "author", "ingredients", "is_favorited", "is_in_shopping_cart", "name", "image", "text", "cooking_time"]

        extra_kwargs = {
            'image': {'required': True}
        }

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return obj.favorites.filter(pk=user.pk).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return obj.groceries_list.filter(pk=user.pk).exists()

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe__amount'),)
        return ingredients

    def recipes_ingredients_tags_create(self, tags, ingredients, recipe):
        recipe.tags.set(tags)
        for i in ingredients:
            RecipesIngredients.objects.create(
                ingredient_id=i.get('id'),
                amount=i.get('amount'),
                recipe=recipe
            )
        return recipe

    def validate(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Необходимо добавить теги.')
        diblicate_tags = []
        for tag in tags:
            if tag in diblicate_tags:
                raise serializers.ValidationError(
                    f'У тега с id {tag} есть дубликат.'
                )
            diblicate_tags.append(tag)
            try:
                Tag.objects.get(id=tag)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(
                    f'Тэк с id {tag} не существует.'
                )

        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо добавить ингредиенты.')
        diblicate_ingredients = []
        for ingredient in ingredients:

            if ingredient['id'] in diblicate_ingredients:
                raise serializers.ValidationError(f'У ингредиента с id {ingredient["id"]} есть дубликат.')
            diblicate_ingredients.append(ingredient['id'])

            if int(ingredient['amount']) < 1:
                raise serializers.ValidationError(
                    'Количество условных единиц ингредиенов не может быть меньше 1.')
            try:
                Ingredient.objects.get(id=ingredient['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(f'Ингредиент с id {ingredient["id"]} не существует.')
        data.update({'author': self.context.get('request').user,
                     'ingredients': ingredients,
                     'tags': tags})
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        return self.recipes_ingredients_tags_create(
            tags, ingredients, recipe
        )

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.recipes_ingredients_tags_create(
            tags, ingredients, instance
        )
        instance.save()
        return instance


class RecipeBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ["id", "name", "image", "cooking_time"]


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class UserSubscriptionsSerializer(UserBasicSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = (request.GET.get('recipes_limit'))
        recipes = obj.recipes.all()
        if recipes_limit is not None:
            recipes_limit=int(recipes_limit)
            recipes = recipes[:recipes_limit]
        return RecipeBriefSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = ["email",
            "id",
            "username",
            "first_name",
            "last_name", "is_subscribed",
            "recipes", "recipes_count"
        ]
