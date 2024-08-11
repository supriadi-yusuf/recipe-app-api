"""
serializer for recipe APIs
"""
from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id','name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe"""

    # add field called tags
    # many=True means this field can contain list of tags
    # required=False means this field is optional
    # tags is read only by default
    # because it is nested serializer
    # (serializer inside serializer)
    tags = TagSerializer(many=True, required=False)

    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link',
                  'tags', # add field tags
                  'ingredients'
                  ]
        read_only_fields = ['id']

    def _get_or_create_tag(self, tags, recipe):
        """Handle getting or creating tag as needed"""
        auth_user = self.context['request'].user
        for tag in tags:
            tab_obj, _ = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )

            recipe.tags.add(tab_obj)

    def _get_or_create_ingredient(self, ingredients, recipe):
        """Handle getting or creating tag as needed"""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, _ = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient
            )

            recipe.ingredients.add(ingredient_obj)

    # overwrite create method
    def create(self, validated_data):
        """Create a recipe"""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])

        recipe = Recipe.objects.create(**validated_data)

        self._get_or_create_tag(tags, recipe)
        self._get_or_create_ingredient(ingredients, recipe)

        return recipe

    # overwrite update method
    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tag(tags, instance)

        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredient(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description', 'image']

class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading image to recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
