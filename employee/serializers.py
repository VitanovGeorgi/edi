from rest_framework import serializers
from .models import Employee, Team, PartialTeamEmployeeRelation

class PartialTeamEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartialTeamEmployeeRelation
        fields = [
            'employee_type',
            'work_arr',
            'employee',
            'team',
        ]


class EmployeeSerializer(serializers.ModelSerializer):
    # adding the foreign key
    partial_team_employee = PartialTeamEmployeeSerializer(many=True, read_only=True)
    class Meta:
        model = Employee
        fields = [
            'name',
            'hourly_rate',
            'employee_id',
            'partial_team_employee',
        ]


class TeamSerializer(serializers.ModelSerializer):
    # adding the foreign key
    partial_team_employee = PartialTeamEmployeeSerializer(many=True, read_only=True)
    class Meta:
        model = Team
        fields = [
            'name',
            'partial_team_employee',
        ]