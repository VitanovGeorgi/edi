from django.contrib import admin
from .models import Employee, Team, PartialTeamEmployeeRelation
# Register your models here.
admin.site.register(Employee)
admin.site.register(Team)
admin.site.register(PartialTeamEmployeeRelation)