from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from helpdesk.forms import UserCreation, WishCreated, CommentCreated, WishUpdateForm
from helpdesk.models import WishList, Comment, TemporaryTokenModel


class Login(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        return '/'


class Register(CreateView):
    form_class = UserCreation
    template_name = 'register.html'
    success_url = '/'


class Logout(LogoutView):
    next_page = '/'
    login_url = 'login/'


class AppView(ListView):
    model = WishList
    paginate_by = 5
    ordering = ['-id']

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            self.template_name = 'index.html'
            return super(AppView, self).get(request)

        else:
            self.template_name = 'AdminIndex.html'
            return super(AppView, self).get(request)

    def paginate_queryset(self, queryset, page_size):
        return_paginate_queryset=super(AppView, self).paginate_queryset(queryset, page_size)
        app_id = []
        for i in return_paginate_queryset[2]:
            print(i.id)
            app_id.append(i.id)
        self.extra_context = {'comment': Comment.objects.filter(application_id__in=app_id)}
        print(self.extra_context)
        return return_paginate_queryset

    def get_queryset(self):
        if not self.request.user.is_superuser:
            queryset = self.model.objects.filter(
                status__in=['NotActive/Confirm', 'NotActive/Reject', 'Active']).filter(author_id=self.request.user.id)
        else:
            queryset = self.model.objects.filter(
                status__in=['Review', 'Active'])
        print(queryset)
        ordering = self.get_ordering()
        queryset = queryset.order_by(*ordering)
        return queryset


class AppCreated(LoginRequiredMixin, CreateView):
    form_class = WishCreated
    template_name = 'appcreated.html'
    success_url = '/'

    def form_valid(self, form):
        if self.request.user.is_superuser:
            raise Exception('You are Admin!\nYou can\'t create This')
        obj = form.save(commit=False)
        obj.author = self.request.user
        obj.save()
        return super().form_valid(form=form)


class CommentCreatedView(LoginRequiredMixin, CreateView):
    form_class = CommentCreated
    template_name = 'comment.html'
    success_url = '/'

    def form_valid(self, form):
        if WishList.objects.get(id=self.kwargs.get(self.pk_url_kwarg)).status == 'Active':
            comment = form.save(commit=False)
            comment.author = self.request.user
            comment.application = WishList.objects.get(id=self.kwargs.get(self.pk_url_kwarg))
            comment.save()
        return super().form_valid(form=form)


class AppUpdateView(LoginRequiredMixin, UpdateView):
    model = WishList
    fields = ['text', 'importance']
    template_name = 'Update.html'
    extra_context = {'Application': WishUpdateForm(),
                     'start':'fsdkjlfkjls'}
    success_url = '/'


class Confirm(LoginRequiredMixin, DeleteView):
    model = WishList
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.status='NotActive/Confirm'
        self.object.save()
        return HttpResponseRedirect(success_url)


class Reject(CreateView):
    form_class = CommentCreated
    template_name = 'comment.html'
    success_url = '/'

    def form_valid(self, form):
        wish_object = WishList.objects.get(id=self.kwargs.get(self.pk_url_kwarg))
        if wish_object.status == 'Active' and self.request.user.is_superuser:
            comment = form.save(commit=False)
            comment.author = self.request.user
            comment.application = wish_object
            comment.last_comment = True
            comment.save()
            wish_object.status = 'NotActive/Reject'
            wish_object.save()
        return super().form_valid(form=form)


class Review(LoginRequiredMixin,DeleteView):
    model = WishList
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        print(self.object)
        success_url = self.get_success_url()
        self.object.status='Review'
        self.object.save()
        return HttpResponseRedirect(success_url)


class DeleteApp(DeleteView):
    model = WishList
    success_url = '/'


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = TemporaryTokenModel.objects.get_or_create(user=user)
        return Response({'token': token.key})
