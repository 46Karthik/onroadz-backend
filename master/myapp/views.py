from django.shortcuts import render  
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from master.views import return_response,upload_image_to_s3,Decode_JWt
from django.shortcuts import get_object_or_404
import base64
from django.core.files.base import ContentFile



class RegisterView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        # check if email or username already exists
        if AuthUser.objects.filter(email=request.data['email']).exists():
            return Response(return_response(0, 'Email already exists'), status=status.HTTP_400_BAD_REQUEST)
        if AuthUser.objects.filter(username=request.data['username']).exists():
            return Response(return_response(0, 'Username already exists'), status=status.HTTP_400_BAD_REQUEST)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(return_response(2, 'Success', serializer.data), status=status.HTTP_201_CREATED)
        return Response(return_response(0, 'Error', serializer.errors), status=status.HTTP_400_BAD_REQUEST)
class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        user = get_object_or_404(AuthUser, id=user_id)
        serializer = RegisterSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": 2, "message": "User updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": 0, "message": "Error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        if not AuthUser.objects.filter(email=email).exists():
            return Response(return_response(0, 'Email not found'), status=status.HTTP_400_BAD_REQUEST)
        user = AuthUser.objects.get(email=email)
        if not user.check_password(password):
            return Response(return_response(0, 'Password not correct'), status=status.HTTP_400_BAD_REQUEST)
        # create token
        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['name'] = user.username
        refresh['role_id'] = user.profile.role
        return Response(return_response(2, 'Login successful', {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }), status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,id = None):
        if id is None:
            get_all_users = ProfileSerializer(Profile.objects.all(), many=True)
            return Response(return_response(2, 'Success', get_all_users.data), status=status.HTTP_200_OK)
        else:
            get_user = ProfileSerializer(Profile.objects.get(id=id))
            return Response(return_response(2, 'Success', get_user.data), status=status.HTTP_200_OK)


class CityWithKmAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id=None):
            if id is None:
                # Get all cities and their related city_km data
                cities = City.objects.all()
                response_data = []

                for city in cities:
                    city_data = CitySerializer(city).data
                    city_km_data = CityKmModel.objects.filter(city=city)
                    city_km_serialized = CityKmModelSerializer(city_km_data, many=True).data

                    response_data.append({
                        "city": city_data,
                        "city_km": city_km_serialized
                    })

                return Response(return_response(2, 'Success', response_data), status=status.HTTP_200_OK)

            else:
                try:
                    # Get a single city and its related city_km data
                    city = City.objects.get(city_id=id)
                    city_data = CitySerializer(city).data
                    city_km_data = CityKmModel.objects.filter(city=city)
                    city_km_serialized = CityKmModelSerializer(city_km_data, many=True).data

                    response_data = {
                        "city": city_data,
                        "city_km": city_km_serialized
                    }

                    return Response(return_response(2, 'Success', response_data), status=status.HTTP_200_OK)

                except CityTable.DoesNotExist:
                    return Response(return_response(0, 'City not found'), status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        city_data = request.data.get('city', {})
        city_km_data = request.data.get('city_km', [])

        # Check if Base64 image is provided
        if 'imageBae64' in city_data:
            city_data['city_image'] = upload_image_Common(city_data['imageBae64'], "city", city_data['cityname'].replace(" ", "") + ".png", "png")

        # Create City
        city_serializer = CitySerializer(data=city_data)
        if city_serializer.is_valid():
            city_instance = city_serializer.save()
        else:
            return Response(return_response(0, 'Error', city_serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        # Create CityKmModel Entries
        for km_data in city_km_data:
            km_data['city'] = city_instance.city_id  # Assign city_id to CityKmModel
            km_serializer = CityKmModelSerializer(data=km_data)
            if km_serializer.is_valid():
                km_serializer.save()
            else:
                return Response(return_response(0, 'Error', km_serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        return Response(return_response(2, 'Success', {'city': city_instance.city_id}), status=status.HTTP_201_CREATED)

    def put(self, request, id):
        try:
            # Get the city instance
            city_instance = City.objects.get(city_id=id)
        except City.DoesNotExist:
            return Response(return_response(0, 'City not found'), status=status.HTTP_404_NOT_FOUND)

        city_data = request.data.get('city', {})
        city_km_data = request.data.get('city_km', [])

        # Update City data
        city_serializer = CitySerializer(city_instance, data=city_data, partial=True)
        if city_serializer.is_valid():
            city_serializer.save()
        else:
            return Response(return_response(0, 'Error', city_serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        # delete  city_km entries filter by city_id
        CityKmModel.objects.filter(city_id=city_instance.city_id).delete()
    
        # Create a new city_km entries
        for city_km_data in city_km_data:
            city_km_data['city'] = city_instance.city_id  # Assign city_id to CityKmModel
            print(city_km_data)

            city_km_serializer = CityKmModelSerializer(data=city_km_data)
            if city_km_serializer.is_valid():
                city_km_serializer.save()
            else:
                return Response(return_response(0, 'Error', city_km_serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        return Response(return_response(2, 'Success', {'city': city_instance.city_id}), status=status.HTTP_200_OK)

def upload_image_Common(file, path,file_name,file_extension):
    # Initialize the boto3 S3 client
    try:
            base64_string = file
            file_extension = (file_extension, "png")  # Default extension

            if not base64_string:
                print("No image provided")
                return None

            # Decode Base64 image
            format_str, img_str = base64_string.split(";base64,")
            content_type = format_str.split(":")[1]
            decoded_file = base64.b64decode(img_str)


            # Convert to file-like object
            file_obj = ContentFile(decoded_file, name=file_name)

            # Upload to S3
            file_url = upload_image_to_s3(file_obj, path, content_type)

            if "Error" in file_url:
                print("Error")
                return None

            return file_url

    except Exception as e:
        print(f"Error: {str(e)}")
        return None
       
    

class UploadBase64ImageAPIView(APIView):
    def post(self, request):
        try:
            base64_string = request.data.get("image")
            file_extension = request.data.get("extension", "png")  # Default extension

            if not base64_string:
                return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)
            file_url = upload_image_Common(base64_string, "city","test001.png", file_extension)
            if file_url:
                return Response({"message": "Upload successful", "file_url": file_url}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Error uploading image"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CityView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
         all_cities = City.objects.all()
         data = CitySerializer(all_cities, many=True).data
         return Response(return_response(2, 'Success', data), status=status.HTTP_200_OK)
       

class HubsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id=None):
        if id is None:
            all_hubs = Hubs.objects.all()
            data = HubsSerializer(all_hubs, many=True).data
            return Response(return_response(2, 'Success', data), status=status.HTTP_200_OK)
        else:
            get_hub = HubsSerializer(Hubs.objects.get(hub_id=id))
            return Response(return_response(2, 'Success', get_hub.data), status=status.HTTP_200_OK)

    def post(self, request):
        payload = Decode_JWt(request.headers.get('Authorization'))
        request.data['created_by'] = payload['name']
        hub_serializer = HubsSerializer(data=request.data)
        if hub_serializer.is_valid():
            hub_serializer.save()
            return Response(return_response(2, 'Success', {'hub': hub_serializer.data}), status=status.HTTP_201_CREATED)
        return Response(return_response(0, 'Error', hub_serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request,id):
        try:
            payload = Decode_JWt(request.headers.get('Authorization'))
            request.data['updated_by'] = payload['name']
            hub_instance = Hubs.objects.get(hub_id=id)
        except Hubs.DoesNotExist:
            return Response(return_response(0, 'Hub not found'), status=status.HTTP_404_NOT_FOUND)
        print(hub_instance)
        hub_serializer = HubsSerializer(hub_instance, data=request.data, partial=True)
        if hub_serializer.is_valid():
            hub_serializer.save()
            return Response(return_response(2, 'Success', {'hub': hub_serializer.data}), status=status.HTTP_200_OK)
        else:
            return Response(return_response(0, 'Error', hub_serializer.errors), status=status.HTTP_400_BAD_REQUEST)

class CarlistView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        all_cars = Car.objects.all()
        data = CarSerializer(all_cars, many=True).data
        return Response(return_response(2, 'Success', data), status=status.HTTP_200_OK)


class CarView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,id = None):
        if id is None:
            all_cars = Car.objects.all()
            response_data = []
            for car in all_cars:
                feet_city_data = FeetCity.objects.filter(car_model_id=car.car_model_id)
                feet_city_serialized = FeetCitySerializer(feet_city_data, many=True).data
                cardata = CarSerializer(car).data
                response_data.append({
                    "car": cardata,
                    "feet_city": feet_city_serialized
                })
            return Response(return_response(2, 'Success', response_data), status=status.HTTP_200_OK)
        else:
            get_car = CarSerializer(Car.objects.get(car_model_id=id))
            feet_city_data = FeetCity.objects.filter(car_model_id=id)

            response_data = {
                "car": get_car.data,
                "feet_city": FeetCitySerializer(feet_city_data, many=True).data
            }
            return Response(return_response(2, 'Success', response_data), status=status.HTTP_200_OK)

    def post(self, request):
        payload = Decode_JWt(request.headers.get('Authorization'))
        car_data = request.data.get('car', {})
        feet_city_data = request.data.get('feet_city', [])
        car_data['created_by'] = payload['name']

        # Check if Base64 image is provided
        if 'imageBae64' in car_data:
            car_data['car_image'] = upload_image_Common(car_data['imageBae64'], "cars", car_data['enter_model_name'].replace(" ", "") + ".png", "png")

        # Create Car
        car_serializer = CarSerializer(data=car_data)
        if car_serializer.is_valid():
            car_instance = car_serializer.save()
        else:
            return Response(return_response(0, 'Error', car_serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        
        # Create FeetCity Entries
        for feet_city_data in feet_city_data:
            feet_city_data['car_model_id'] = car_instance.car_model_id  # Assign car_model_id to FeetCity
            feet_city_serializer = FeetCitySerializer(data=feet_city_data)
            if feet_city_serializer.is_valid():
                feet_city_serializer.save()
            else:
                return Response(return_response(0, 'Error', feet_city_serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        return Response(return_response(2, 'Success', {'car': car_serializer.data}), status=status.HTTP_201_CREATED)

    def put(self, request, id):
        payload = Decode_JWt(request.headers.get('Authorization'))
        try:
            # Get the car instance
            car_instance = Car.objects.get(car_model_id=id)
        except Car.DoesNotExist:
            return Response(return_response(0, 'Car not found'), status=status.HTTP_404_NOT_FOUND)

        car_data = request.data.get('car', {})
        car_data['updated_by'] = payload['name']
        feet_city_data = request.data.get('feet_city', [])
        
        # upload image
        # Check if Base64 image is provided
        if 'imageBae64' in car_data:
            car_data['car_image'] = upload_image_Common(car_data['imageBae64'], "cars", car_data['enter_model_name'].replace(" ", "") + ".png", "png")
       

        # Update Car data
        car_serializer = CarSerializer(car_instance, data=car_data, partial=True)
        if car_serializer.is_valid():
            car_serializer.save()
        else:
            return Response(return_response(0, 'Error', car_serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        # delete feet_city_data entries filter by car_model_id
        FeetCity.objects.filter(car_model_id=car_instance.car_model_id).delete()
        # Update or Create FeetCity Entries
        for feet_city_data in feet_city_data:
            feet_city_data['car_model_id'] = car_instance.car_model_id  # Assign car_model_id to FeetCity
            feet_city_serializer = FeetCitySerializer(data=feet_city_data)
            if feet_city_serializer.is_valid():
                feet_city_serializer.save()
            else:
                return Response(return_response(0, 'Error', feet_city_serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        return Response(return_response(2, 'Success', {'car': car_instance.car_model_id}), status=status.HTTP_200_OK)

class ProviderView(APIView):
    def get(self, request,id = None):
        if id is None:
            provider_serializer = ProviderSerializer(Provider.objects.all(), many=True)
            return Response(return_response(2, 'Success', provider_serializer.data), status=status.HTTP_200_OK)
        else:
            provider_instance = Provider.objects.get(provider_id=id)
            provider_serializer = ProviderSerializer(provider_instance)
            return Response(return_response(2, 'Success', provider_serializer.data), status=status.HTTP_200_OK)
    
    def post(self, request):
        if 'imageBae64' in request.data:
            request.data['agreement_path'] = upload_image_Common(request.data['imageBae64'], "provider", request.data['name'].replace(" ", "") + ".png", "png")
        provider_serializer = ProviderSerializer(data=request.data)
        if provider_serializer.is_valid():
            provider_serializer.save()
            return Response(return_response(2, 'Success', {'provider': provider_serializer.data}), status=status.HTTP_200_OK)
        else:
            return Response(return_response(0, 'Error', provider_serializer.errors), status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, id):
        if 'imageBae64' in request.data:
            request.data['agreement_path'] = upload_image_Common(request.data['imageBae64'], "provider", request.data['name'].replace(" ", "") + ".png", "png")
        provider_instance = Provider.objects.get(provider_id=id)
        provider_serializer = ProviderSerializer(provider_instance, data=request.data, partial=True)
        if provider_serializer.is_valid():
            provider_serializer.save()
            return Response(return_response(2, 'Success', {'provider': provider_serializer.data}), status=status.HTTP_200_OK)
        else:
            return Response(return_response(0, 'Error', provider_serializer.errors), status=status.HTTP_400_BAD_REQUEST)


class FleetView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,id= None):
        if id is None:
            all_feet = Fleet.objects.all()
            serializer = FeetSerializer(all_feet, many=True)
            return Response(return_response(2, 'Success', serializer.data), status=status.HTTP_200_OK)
        else:
            get_feet = FeetSerializer(Fleet.objects.get(feet_id=id))
            feet_document_data = FleetDocument.objects.filter(feet_id=id)
            response_data = {
                "feet": get_feet.data,
                "feet_document": FeetDocumentSerializer(feet_document_data, many=True).data
            }
            return Response(return_response(2, 'Success', response_data), status=status.HTTP_200_OK)

    def post(self, request):
        payload = Decode_JWt(request.headers.get('Authorization'))
        feet_data = request.data.get('feet', {})
        feet_document_data = request.data.get('feet_document', [])
        feet_data['created_by'] = payload['name']

        # Create Feet
        feet_serializer = FeetSerializer(data=feet_data)
        if feet_serializer.is_valid():
            feet_instance = feet_serializer.save()
        else:
            return Response(return_response(0, 'Error', feet_serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        
        # Create FeetDocument Entries
        for feet_document_data in feet_document_data:
            # if imagebase64 found upload image
            if 'imageBae64' in feet_document_data:
                feet_document_data['upload_document_text'] = upload_image_Common(feet_document_data['imageBae64'], "feetdocument", feet_document_data['document_number'].replace(" ", "") + ".png", "png")
            feet_document_data['feet_id'] = feet_instance.feet_id  # Assign feet_id to FeetDocument
            feet_document_serializer = FeetDocumentSerializer(data=feet_document_data)
            if feet_document_serializer.is_valid():
                feet_document_serializer.save()
            else:
                return Response(return_response(0, 'Error', feet_document_serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        return Response(return_response(2, 'Success', {'feet': feet_serializer.data}), status=status.HTTP_201_CREATED)

    def put(self, request, id):
        payload = Decode_JWt(request.headers.get('Authorization'))
        try:
            # Get the feet instance
            feet_instance = Fleet.objects.get(feet_id=id)
        except Fleet.DoesNotExist:
            return Response(return_response(0, 'Feet not found'), status=status.HTTP_404_NOT_FOUND)

        feet_data = request.data.get('feet', {})
        feet_data['updated_by'] = payload['name']
        feet_document_data = request.data.get('feet_document', [])
        
        # Update Feet data
        feet_serializer = FeetSerializer(feet_instance, data=feet_data, partial=True)
        if feet_serializer.is_valid():
            feet_serializer.save()
        else:
            return Response(return_response(0, 'Error', feet_serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        # delete feet_document_data entries filter by feet_id
        FleetDocument.objects.filter(feet_id=feet_instance.feet_id).delete()
        # Update or Create FeetDocument Entries
        for feet_document_data in feet_document_data:
            # if imagebase64 found upload image
            if 'imageBae64' in feet_document_data:
                feet_document_data['upload_document_text'] = upload_image_Common(feet_document_data['imageBae64'], "feetdocument", feet_document_data['document_number'].replace(" ", "") + ".png", "png")
            feet_document_data['feet_id'] = feet_instance.feet_id  # Assign feet_id to FeetDocument
            feet_document_serializer = FeetDocumentSerializer(data=feet_document_data)
            if feet_document_serializer.is_valid():
                feet_document_serializer.save()
            else:
                return Response(return_response(0, 'Error', feet_document_serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        return Response(return_response(2, 'Success', {'feet': feet_instance.feet_id}), status=status.HTTP_200_OK)