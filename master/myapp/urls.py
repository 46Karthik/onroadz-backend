from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('userlist/', UserView.as_view(), name='user'),
    path('user/<int:id>/', UserView.as_view(), name='user'),
    path('useredit/<int:user_id>/', UpdateUserView.as_view(), name='update_user'),
    path('city/', CityWithKmAPIView.as_view(), name='city_add'),
    path('cityList/', CityView.as_view(), name='city'),
    path('city/<int:id>/', CityWithKmAPIView.as_view(), name='city_add'),
    path('uploadimage/', UploadBase64ImageAPIView.as_view(), name='upload_image'),
    path('hubs/', HubsView.as_view(), name='hubs'),
    path('hubs/<int:id>/', HubsView.as_view(), name='hubs'),
    path('car/', CarView.as_view(), name='car'),
    path('carList/', CarlistView.as_view(), name='car'),
    path('car/<int:id>/', CarView.as_view(), name='car'),
    path('provider/', ProviderView.as_view(), name='provider'),
    path('provider/<int:id>/', ProviderView.as_view(), name='provider'),
    path('feet/', FleetView.as_view(), name='feet'),
    path('feet/<int:id>/', FleetView.as_view(), name='feet'),
]

