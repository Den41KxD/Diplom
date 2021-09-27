from rest_framework import serializers
from rest_framework import exceptions
from helpdesk.models import User, WishList, Comment


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = ['title', 'text', 'created_at', 'status', 'importance']

    def create(self, validated_data):
        request = self.context.get('request')
        if request.user.is_superuser:
            raise exceptions.ValidationError('You Admin!! You can\'t create ')
        new_app = WishList.objects.create(**validated_data, author=request.user)
        new_app.save()
        return new_app


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text', 'application']

    def create(self, validated_data):
        request = self.context.get('request')
        new_comment = Comment.objects.create(**validated_data, author=request.user)
        if not request.user.is_superuser:
            if new_comment.application.author != request.user:
                raise exceptions.ValidationError('You can\'t comment this app')
        if new_comment.application.status != 'Active':
            raise exceptions.ValidationError('You can comment: App not active')
        new_comment.save()
        return new_comment


class AppSerializerList(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = ['id', 'title', 'text', 'created_at', 'status', 'importance', 'author']
