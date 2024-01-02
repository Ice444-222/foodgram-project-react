from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=256, unique=True, verbose_name="Название")
    color = models.CharField(max_length=16, unique=True, verbose_name="Цвет")
    slug = models.SlugField(
        max_length=50, unique=True, verbose_name="Уникальный слаг"
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField( max_length=256, verbose_name="Название ингредиента")
    measurement_unit = models.CharField( max_length=30, verbose_name="Единица измерения")

    class Meta:
        unique_together = ('name', 'measurement_unit')
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
    
    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes", verbose_name="Автор"
    )
    name = models.CharField(max_length=200, verbose_name="Название рецепта")
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False,
        null=False,
        verbose_name="Картинка"
    )
    text = models.TextField(
        verbose_name="Описание"
    )
    ingredients = models.ManyToManyField(Ingredient, through='RecipesIngredients', related_name='recipes',  verbose_name="Ингредиенты")
    tags = models.ManyToManyField(Tag, related_name='recipes', verbose_name="Теги")
    cooking_time = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Время готовки", )
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    favorites = models.ManyToManyField(
        User,
        related_name="favorites",
        blank=True,
        verbose_name="Избранное"
    )
    groceries_list = models.ManyToManyField(
        User,
        related_name="groceries_list",
        blank=True,
        verbose_name="Список покупок",
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

        


class RecipesIngredients(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredient', verbose_name="Рецепт")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipe', verbose_name="Ингредиент")
    amount = models.IntegerField(verbose_name='Количество')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipeingredient_unique')]
        verbose_name = 'рецепт и ингредиент'
        verbose_name_plural = 'Рецепты и ингредиенты'



