from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.

class Iiqa(models.Model):
    STATE_CHOICES = (
        ("---", "---"),
        ("Andhra Pradesh", "Andhra Pradesh"),
        ("Arunachal Pradesh", "Arunachal Pradesh"),
        ("Assam", "Assam"),
        ("Bihar", "Bihar"),
        ("Chhattisgarh", "Chhattisgarh"),
        ("Goa", "Goa"),
        ("Gujarat", "Gujarat"),
        ("Haryana", "Haryana"),
        ("Himachal Pradesh", "Himachal Pradesh"),
        ("Jharkhand", "Jharkhand"),
        ("Karnataka", "Karnataka"),
        ("Kerala", "Kerala"),
        ("Madhya Pradesh", "Madhya Pradesh"),
        ("Maharashtra", "Maharashtra"),
        ("Manipur", "Manipur"),
        ("Meghalaya", "Meghalaya"),
        ("Mizoram", "Mizoram"),
        ("Nagaland", "Nagaland"),
        ("Odisha", "Odisha"),
        ("Punjab", "Punjab"),
        ("Rajasthan", "Rajasthan"),
        ("Sikkim", "Sikkim"),
        ("Tamil Nadu", "Tamil Nadu"),
        ("Telangana", "Telangana"),
        ("Tripura", "Tripura"),
        ("Uttar Pradesh", "Uttar Pradesh"),
        ("Uttarakhand", "Uttarakhand"),
        ("Gairsain", "Gairsain"),
        ("West Bengal", "West Bengal")
    )

    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))

    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    head = models.CharField(max_length=100, null=True)
    designation = models.CharField(max_length=100, null=True)
    own_campus = models.BooleanField(choices=BOOL_CHOICES, default=False)
    phn_no_clg = PhoneNumberField(null=False, blank=False)
    phn_no_principal = PhoneNumberField(null=False, blank=False)
    phn_no_principal_alt = PhoneNumberField(null=False, blank=False)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, choices=STATE_CHOICES, default=1, null=True)
    pincode = models.CharField(max_length=100, null=True)
    autonomous_status_date = models.CharField(max_length=100, null=True)
    institution_type = models.CharField(max_length=100, null=True)
    location = models.CharField(max_length=100, null=True)
    financial_status = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)


class Ssr_Text_Converter(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    clg_name = models.CharField(max_length=100, null=True)
    uni_name = models.CharField(max_length=100, null=True)
    pdf = models.FileField(null=True, blank=True)
    status = models.CharField(default='None', max_length=100, null=True)

    def __str__(self):
        return str(self.user)


class Ssr_Geo_Tag(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    img = models.ImageField(null=True, blank=True)
    latitude = models.CharField(max_length=100, null=True)
    longitude = models.CharField(max_length=100, null=True)
    lat_convert = models.CharField(max_length=100, null=True)
    long_convert = models.CharField(max_length=100, null=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)