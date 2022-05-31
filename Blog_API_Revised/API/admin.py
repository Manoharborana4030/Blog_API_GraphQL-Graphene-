from django.contrib import admin
from django.apps import apps
from .models import *
# Register your models here.

app = apps.get_app_config('graphql_auth')
admin.site.register(AccessToken)
admin.site.register(Post)
admin.site.register(Comments)
for model_name, model in app.models.items():
    admin.site.register(model)