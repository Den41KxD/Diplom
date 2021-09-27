from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
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
        self.extra_context = {'comment': Comment.objects.all()}
        if not request.user.is_superuser:
            self.template_name = 'index.html'
            return super(AppView, self).get(request)

        else:
            self.template_name = 'AdminIndex.html'
            return super(AppView, self).get(request)


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
    extra_context = {'Application': WishUpdateForm()}
    success_url = '/'


# class Confirm(DeleteView):
#     model = WishList
#     success_url = '/'
#
#     def delete(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         success_url = self.get_success_url()
#         self.object.status='NotActive/Confirm'
#         self.object.save()
#         return HttpResponseRedirect(success_url)

@action(detail=True, methods=['post'])
def confirm(request, *args, **kwargs):
    if not request.user.is_superuser:
        raise Exception('You are not Admin!!')
    confirm_obj = WishList.objects.get(pk=kwargs.get('pk'))
    if confirm_obj.status in ['Active', 'Review']:
        confirm_obj.status = 'NotActive/Confirm'
        confirm_obj.save()
        return HttpResponseRedirect('/')
    else:
        raise Exception('Can\'t confirm inactive Wish')


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


# class Review(LoginRequiredMixin,DeleteView):
#     model = WishList
#     success_url = '/'
#     def delete(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         print(self.object)
#         success_url = self.get_success_url()
#         self.object.status='Review'
#         self.object.save()
#         return HttpResponseRedirect(success_url)


@action(detail=True, methods=['post'])
def review(request, *args, **kwargs):
    if request.user.is_superuser:
        raise Exception('You are Admin!!')
    review_obj = WishList.objects.get(pk=kwargs.get('pk'))
    if review_obj.status in ['NotActive/Reject', ]:
        review_obj.status = 'Review'
        review_obj.save()
        return HttpResponseRedirect('/')
    else:
        raise Exception('Can\'t review This Wish')


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
