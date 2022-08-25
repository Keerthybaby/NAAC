from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Iiqa)
admin.site.register(Ssr_Text_Converter)
admin.site.register(Ssr_Geo_Tag)
admin.site.register(Ssr_Plot)