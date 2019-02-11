from cloud_api.views import TokenView, StatusCodeView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from face_recognition.views import FaceView, AvatarView
from finder.views import FinderView
from photo_load.views import PhotoView
from rest_framework import routers
from web.views import index

from .views import sign_in, sign_out, sign_up

router = routers.SimpleRouter()
router.register(r'api/photos', PhotoView, base_name='photos')
router.register(r'api/faces', FaceView, base_name='faces')
router.register(r'api/avatars', AvatarView, base_name='avatars')
router.register(r'api/cloud-status', StatusCodeView, base_name='cloud-status')
router.register(r'api/tokens', TokenView, base_name='tokens')
router.register(r'api/find', FinderView, base_name='find')

urlpatterns = [
    path(r'', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/sign_in/', sign_in),
    path('api/sign_up/', sign_up),
    path('api/sign_out/', sign_out),
    path('', index),
    path('<path>', index),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
