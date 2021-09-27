from django.urls import path, include
from rest_framework.routers import SimpleRouter

from API.resorces import UserViewSet, AppViewSet, CommentViewSet
from helpdesk.views import Login, Register, Logout, AppView, AppCreated, CommentCreatedView, AppUpdateView, \
    Reject, DeleteApp, CustomAuthToken, confirm, review

router = SimpleRouter()
router.register('user', UserViewSet)
router.register('app', AppViewSet)
router.register('comment', CommentViewSet)


urlpatterns = [

    path('comment/<int:pk>/', CommentCreatedView.as_view(), name='comment'),
    path('update/<int:pk>/', AppUpdateView.as_view(), name='update'),
    path('', AppView.as_view(), name='index'),
    path('createapp/', AppCreated.as_view(), name='appcreated'),
    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('logout/', Logout.as_view(), name='logout'),
    path('confirm/<int:pk>/', confirm, name='confirm'),
    path('reject/<int:pk>/', Reject.as_view(), name='reject'),
    path('review/<int:pk>/', review, name='review'),
    path('delete/<int:pk>/', DeleteApp.as_view(), name='delete'),
    path('api/', include(router.urls)),
    path('api-auth/', CustomAuthToken.as_view())
]
