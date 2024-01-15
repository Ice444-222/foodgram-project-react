import base64

from django.contrib.auth import get_user_model
from django.core.exceptions import BadRequest, ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, Recipe, RecipesIngredients, Tag

User = get_user_model()
MIN_INGREDIENT_AMOUNT = 1
MAX_RECIPES_PER_PAGE = 6


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
        if current_password != user.password:
            raise serializers.ValidationError('Неверный текущий пароль.')
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
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ["id", "tags", "author", "ingredients",
                  "is_favorited", "is_in_shopping_cart",
                  "name", "image", "text", "cooking_time"]

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe__amount'),)
        return ingredients

    @staticmethod
    def recipes_ingredients_tags_create(tags, ingredients, recipe):
        with transaction.atomic():
            recipe.tags.set(tags)
            recipe_ingredients = [
                RecipesIngredients(
                    ingredient_id=i.get('id'),
                    amount=i.get('amount'),
                    recipe=recipe
                )
                for i in ingredients
            ]
            RecipesIngredients.objects.bulk_create(recipe_ingredients)
        return recipe

    def validate_tags(self):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Необходимо добавить теги.')
        unique_tags = set(tags)
        if len(unique_tags) < len(tags):
            raise serializers.ValidationError(
                'В списке есть теги дубликаты.'
            )
        for tag in tags:
            try:
                Tag.objects.get(id=tag)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(
                    f'Тэг с id {tag} не существует.'
                )
        return tags

    def validate_ingredients(self):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо добавить ингредиенты.')
        diblicate_ingredients = []
        for ingredient in ingredients:
            if ingredient['id'] in diblicate_ingredients:
                raise serializers.ValidationError(
                    f'У ингредиента с id {ingredient["id"]} есть дубликат.'
                )
            diblicate_ingredients.append(ingredient['id'])
            if int(ingredient['amount']) < 1:
                raise serializers.ValidationError(
                    'Количество условных единиц '
                    'ингредиенов не может быть меньше 1.'
                )
            try:
                Ingredient.objects.get(id=ingredient['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f'Ингредиент с id {ingredient["id"]} не существует.'
                )
        return ingredients

    def validate(self, data):
        data.update({'author': self.context.get('request').user,
                     'ingredients': self.validate_ingredients(),
                     'tags': self.validate_tags()})
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
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit is not None and recipes_limit.isdigit():
            recipes_limit = int(recipes_limit)
        else:
            recipes_limit = MAX_RECIPES_PER_PAGE
        recipes = recipes[:recipes_limit]
        return RecipeBriefSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name", "is_subscribed",
            "recipes", "recipes_count"
        ]
