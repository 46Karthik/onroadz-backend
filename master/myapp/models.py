from django.db import models
from django.contrib.auth.models import User as AuthUser


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Role name

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    role = models.IntegerField(default=0)  # Role field without choices
    is_admin = models.BooleanField(default=False)
    is_active = models.IntegerField(default=2)

    def __str__(self):
        return f"{self.name} - Role: {self.role}"

class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    cityname = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    location_id = models.CharField(max_length=255)
    city_image = models.TextField()
    is_active = models.IntegerField(default=1)
    enable_car_delivery_is_active = models.IntegerField(default=0)
    
    select_default_pricing_model = models.CharField(max_length=255, null=True, blank=True)
    select_default_pricing_model_is_active = models.IntegerField(default=0)
    
    per_km_model_is_active = models.IntegerField(default=0)
    packaging_type = models.CharField(max_length=255, null=True, blank=True)
    
    weekend_start_day = models.CharField(max_length=50, null=True, blank=True)
    weekend_start_time = models.TimeField( null=True, blank=True)
    weekend_end_day = models.CharField(max_length=50, null=True, blank=True)
    weekend_end_time = models.TimeField( null=True, blank=True)
    
    operational_hours_start_time = models.TimeField()
    operational_hours_end_time = models.TimeField()
    
    def __str__(self):
        return self.cityname

class CityKmModel(models.Model):
    city_model_id = models.AutoField(primary_key=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    package_name = models.CharField(max_length=255, null=True, blank=True)
    plan_provider = models.CharField(max_length=255 , null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    default_is_active = models.IntegerField(default=0)
    enable_is_active = models.IntegerField(default=0)
    
    def __str__(self):
        return self.package_name

class Hubs(models.Model):
    hub_id = models.AutoField(primary_key=True)
    city_id = models.IntegerField()
    city_name = models.CharField(max_length=100)
    hub_name = models.CharField(max_length=100)
    hub_type = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.IntegerField(default=1)
    created_by = models.CharField(max_length=100)
    updated_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True,blank=True)

    def __str__(self):
        return self.hub_name

class Car(models.Model):
    car_model_id = models.AutoField(primary_key=True)
    feet_type = models.CharField(max_length=100)
    enter_model_name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    tank_capacity = models.DecimalField(max_digits=10, decimal_places=2)
    categoty = models.CharField(max_length=100)  # Note: consider renaming to "category"
    seater = models.IntegerField()
    transmission = models.CharField(max_length=50)
    fuel_type = models.CharField(max_length=50)
    milage = models.DecimalField(max_digits=10, decimal_places=2)
    luggage_carrier = models.CharField(max_length=100)
    varient = models.CharField(max_length=100, null=True, blank=True)  # Note: consider renaming to "variant"
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charage = models.DecimalField(max_digits=10, decimal_places=2)  # Consider "delivery_charge"
    description = models.TextField(null=True,blank=True)
    car_image = models.CharField(max_length=200,null=True,blank=True)  # Alternatively, use models.URLField() or models.ImageField()
   # common below fileds
    is_active = models.IntegerField(default=1)
    created_by = models.CharField(max_length=100)
    updated_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True,blank=True)

    def __str__(self):
        return self.enter_model_no

class FeetCity(models.Model):
    feet_city_id = models.AutoField(primary_key=True)
    city_id = models.IntegerField()
    city_name = models.CharField(max_length=100)
    car_model_id = models.ForeignKey(Car, on_delete=models.CASCADE)

    def __str__(self):
        return self.city_name


class Provider(models.Model):
    provider_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=50)
    city = models.CharField(max_length=255)
    supplier_type = models.CharField(max_length=255)
    agreement_id = models.CharField(max_length=255, unique=True)
    agreement_path = models.CharField(max_length=200,null=True,blank=True)
    valid_till_date = models.DateField()
    provider_address = models.CharField(max_length=255,null=True,blank=True)
    provider_city = models.CharField(max_length=255)
    provider_state = models.CharField(max_length=255)
    provider_country = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    contact_mobile = models.CharField(max_length=15)
    contact_email = models.EmailField(unique=True)
    contact_designation = models.CharField(max_length=255,null=True,blank=True)
    is_active = models.IntegerField(default=1)

    def __str__(self):
        return self.name

class Fleet(models.Model):
    feet_id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=255)
    city_id = models.IntegerField()
    car_model_id = models.IntegerField()
    car_model_name = models.CharField(max_length=255)
    color = models.CharField(max_length=50)
    provider_type = models.CharField(max_length=255)
    provider_id = models.IntegerField()
    provider_name = models.CharField(max_length=255)
    hub_id = models.IntegerField()
    hub_name = models.CharField(max_length=255)
    registration_no = models.CharField(max_length=50, unique=True)
    chassis_number = models.CharField(max_length=255)
    engine_number = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.car_model_name} - {self.registration_no}"

class FleetDocument(models.Model):
    feet_document_id = models.AutoField(primary_key=True)
    feet_id = models.ForeignKey(Fleet, on_delete=models.CASCADE, related_name='documents')
    car_document_type = models.CharField(max_length=255)
    upload_document_text = models.TextField()
    document_number = models.CharField(max_length=100, unique=True)
    valid_till_date = models.DateField()

    def __str__(self):
        return f"{self.car_document_type} - {self.document_number}"