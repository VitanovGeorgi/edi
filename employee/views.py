from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework_swagger import renderers
from .models import Employee, Team, PartialTeamEmployeeRelation as TERelation
# from .serializers import EmployeeSerializer, TeamSerializer, PartialTeamEployeeSerializer

# Create your views here.
