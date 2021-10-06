from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from API.serializers import UserSerializers, AppSerializer, AppSerializerList, CommentSerializer
from helpdesk.models import User, WishList, Comment


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializers
    queryset = User.objects.all()


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()


class AppViewSet(ModelViewSet):
    serializer_class = AppSerializer
    queryset = WishList.objects.all()
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def get_comment(count):
        comment_dict = {}
        all_com = Comment.objects.filter(application_id=count)
        count2 = 0
        for i in all_com:
            count2 += 1
            comment_dict.update({str(count2)+': '+i.author.username: i.text})
        return comment_dict

    def list(self, request, *args, **kwargs):
        self.serializer_class = AppSerializerList
        if request.user.is_superuser:
            if not self.request.query_params.get('importance'):
                queryset = self.filter_queryset(self.queryset.filter(status__in=['Active', 'Review']))
            else:
                queryset = self.filter_queryset(self.queryset.filter(status__in=['Active', 'Review'],
                                                importance=self.request.query_params.get('importance').capitalize()))
                # queryset = self.filter_queryset(self.queryset.filter(
                #     importance=self.request.query_params.get('importance')))
        else:
            queryset = self.filter_queryset(self.queryset.filter(author_id=self.request.user.id,
                                            status__in=['Active', 'NotActive/Reject', 'NotActive/Confirm']))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        for i in serializer.data:
            i.update({'Comment': self.get_comment(i.get('id'))})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise exceptions.ValidationError('You are not Admin!!')
        confirm_obj = self.get_object()
        if confirm_obj.status in ['Active','Review']:
            confirm_obj.status = 'NotActive/Confirm'
            confirm_obj.save()
            serializer = self.get_serializer(confirm_obj)
            return Response(serializer.data)
        else:
            raise exceptions.ValidationError('Can\'t confirm inactive application')

    @action(detail=True, methods=['post'])
    def reject(self, *args, **kwargs):
        reject_obj = self.get_object()
        if not self.request.user.is_superuser:
            raise exceptions.ValidationError('You are not Admin!!')
        elif len(self.request.data) != 1 or not self.request.data.get('comment'):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif reject_obj.status == 'Review':
            reject_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        reject_obj.status = 'NotActive/Reject'
        reject_obj.save()
        Comment.objects.create(last_comment=True,
                               text=self.request.data.get('comment'),
                               application_id=reject_obj.id,
                               author_id=self.request.user.id)

        serializer = self.get_serializer(reject_obj)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def review(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            review_obj = self.get_object()
            review_obj.status = 'Review'
            review_obj.save()
            serializer = self.get_serializer(review_obj)
            return Response(serializer.data)
