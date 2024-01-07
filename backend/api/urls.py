from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomTokenObtainPairView

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                    TokenLogoutView, UserViewSet)

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("tags", TagViewSet, basename="tags")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("ingredients", IngredientViewSet, basename="ingredients")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "auth/token/login/", CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("auth/token/logout/", TokenLogoutView.as_view(), name='token_logout'),
]
