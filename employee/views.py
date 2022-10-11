from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework_swagger import renderers
from .models import Employee, Team, PartialTeamEmployeeRelation as TERelation, total_work_arr
from .serializers import EmployeeSerializer, TeamSerializer, PartialTeamEmployeeSerializer
from .exceptions import EmployeeFloatError, EmployeeStrError

# Create your views here.

# region Employee

@api_view(['GET', 'POST'])
def employee_api(request):
    qs = Employee.objects.all()

    if request.method == 'GET':
        '''
            If there's a query param employee_id [str] corresponding to Employee.employee_id
            then return only that employee, o.w. return all employees
        '''
        query_id = request.query_params.get('employee_id', None)
        if query_id is not None:
            employee = get_object_or_404(qs.filter(employee_id=query_id))
            serializer = EmployeeSerializer(instance=employee)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = EmployeeSerializer(instance=qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = EmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response({'message': 'invalid request'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def employee_api_pk(request, pk):
    qs = Employee.objects.all()

    if request.method == 'PUT':
        query_employee = qs.filter(employee_id=pk)
        serializer = EmployeeSerializer(data=request.data)

        if 'name' in request.data:
            if isinstance(request.data['name'], str): # ensuring that the user enters a str for name
                query_employee.update(name=request.data['name'])
            else:
                raise EmployeeStrError(request.data['name'])
            
        if 'hourly_rate' in request.data:
            if isinstance(request.data['hourly_rate'], float): # ensuring that the user enters a float for hourly_rate
                query_employee.update(hourly_rate=request.data['hourly_rate'])
            else:
                raise EmployeeFloatError(request.data['hourly_rate'])

        if 'employee_id' in request.data:
            if isinstance(request.data['employee_id'], str):
                query_employee.update(employee_id=request.data['employee_id'])
            else:
                # going to be using serializers.ValidationError since they appear nicer on screen and are somewhat appropriate
                # also got tired of creating a custom error for everything
                raise serializers.ValidationError(f'employee_id needs to be a string')

        return Response(request.data, status=status.HTTP_204_NO_CONTENT)

    if request.method == 'DELETE':
        query_employee = qs.filter(employee_id=pk)
        if not query_employee.exists():
            return Response({'message': f'Employee {pk} does not exist.'}, status=status.HTTP_204_NO_CONTENT)
        query_employee.delete()
        return Response({'message': f'Employee {pk} deleted.'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'message': 'invalid request'}, status=status.HTTP_400_BAD_REQUEST)

# endregion



# region Team

@api_view(['GET', 'POST'])
def team_api(request):
    qs = Team.objects.all()

    if request.method == 'GET':
        ''' 
            Will return either all teams, or if given a query param name [str] will return that specific team.
        '''
        query_name = request.query_params.get('name', None)
        if query_name is not None:
            team = get_object_or_404(qs.filter(name=query_name))
            serializer = TeamSerializer(instance=team)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        serializer = TeamSerializer(instance=qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = TeamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response({'message': 'invalid request'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
def team_api_pk(request, pk):
    qs = Team.objects.all()

    if request.method == 'PUT':
        # returns a QuerySet object of Team objects, but doesn't matter since there is uniqueness enforced
        query_team = qs.filter(name=pk) 
        serializer = TeamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query_team.update(name=request.data['name'])
        return Response(request.data, status=status.HTTP_204_NO_CONTENT)

    if request.method == 'DELETE':
        query_team = qs.filter(name=pk)
        if not query_team.exists():
            return Response({'message': f'Team {pk} does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        query_team.delete()
        return Response({'message': f'Team {pk} deleted.'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'message': 'invalid request.'}, status=status.HTTP_204_NO_CONTENT)

# endregion


# region PartialTeamEmployeeRelation

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
def team_employee_api(request):
    qs = TERelation.objects.all()
    '''
        Won't be using url params for put and delete, rather it'll use query params.
    '''
    if request.method == 'GET':
        query_id = request.query_params.get('employee_id', None)

        if query_id is not None:

            employee = Employee.objects.filter(employee_id=query_id).first()
            if employee is None:
                raise serializers.ValidationError('No employee with such id.')
            
            team_employees = qs.filter(employee=employee)
            if not team_employees.exists():
                raise serializers.ValidationError('This employee is not assigned to any team.')

            serializer = PartialTeamEmployeeSerializer(instance=team_employees, many=True)
            # PartialTeamEmployeeRelation is saved with internal values for the foreign keys, not the user defined
            # unfortuantely this returns objects in the form of {'employee': 'employee.id', 'team': 'team.id'} - internal keys
            # which aren't really readable for the user, so we're converting them to the user inputted
            for val in serializer.data:
                val['employee'] = Employee.objects.filter(id=val['employee']).first().employee_id
                val['team'] = Team.objects.filter(id=val['team']).first().name
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = PartialTeamEmployeeSerializer(instance=qs, many=True)
        for val in serializer.data:
                val['employee'] = Employee.objects.filter(id=val['employee']).first().employee_id
                val['team'] = Team.objects.filter(id=val['team']).first().name
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        input_data = request.data

        if 'employee' not in request.data:
            raise serializers.ValidationError('Please enter an employee id.')

        if not isinstance(request.data['employee'], str):
            raise serializers.ValidationError('Please enter a valid employee id, a string.')
        
        employee = Employee.objects.filter(employee_id=request.data['employee']).first()
        if employee is None:
            raise serializers.ValidationError('No employee with this id.')
        # finally replacing the input employee_id [char] with the internal id        
        input_data['employee'] = employee.id

        if 'team' not in request.data:
            raise serializers.ValidationError('Please enter a team.')
        
        if not isinstance(request.data['team'], str):
            raise serializers.ValidationError('Please enter a valid team name, a string.')

        team = Team.objects.filter(name=request.data['team']).first()
        if team is None:
            raise serializers.ValidationError('No team with this name.')

        input_data['team'] = team.id

        serializer = PartialTeamEmployeeSerializer(data=input_data)
        # to validate the remaining of the request.data fields
        serializer.is_valid(raise_exception=True)

        # validating that the input hours aren't going to take the employee over the maximum allowed
        employee_relations = TERelation.objects.filter(employee=employee.id)
        total_hours = 0
        hours_prior_to_update = serializer.validated_data['work_arr']
        for relation in employee_relations:
            total_hours += relation.work_arr

        if total_hours + request.data['work_arr'] - hours_prior_to_update > total_work_arr:
            raise serializers.ValidationError(f'Employee {employee.name} cannot work more than {total_work_arr} hours/week, exceeding by {total_hours + request.data["work_arr"] - hours_prior_to_update - total_work_arr}')

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == 'PUT':
        '''
            In order to identify the relation, the user has to provide employee_pk and team_pk. If it wishes
            to update them, then it has to provide employee_update, team_update. employee_pk and employee_update
            are the employee_id in Employee, and team_pk and team_update are the name in Team.
            For the other fields it only has to provide the normal field names, i.e. work_arr, and employee_type.
        '''
        employee_pk = request.data['employee_pk']
        team_pk = request.data['team_pk']
        if employee_pk is None:
            raise serializers.ValidationError('Please provide an employee_pk.')
        if not isinstance(employee_pk, str):
            raise serializers.ValidationError('Please provide a valid employee_pk, a string.')
        if team_pk is None:
            raise serializers.ValidationError('Please provide a team_pk.')
        if not isinstance(team_pk, str):
            raise serializers.ValidationError('Please provide a valid team_pk, a string.')

        if not Employee.objects.filter(employee_id=employee_pk).exists():
            raise serializers.ValidationError(f'Employee with {employee_pk} does not exist.')
        if not Team.objects.filter(name=team_pk).exists():
            raise serializers.ValidationError(f'Team {team_pk} does not exist.')
        # not using .first() here since, .update() won't work afterwards
        query_relation = qs.filter(
            employee=Employee.objects.get(employee_id=employee_pk),
            team=Team.objects.get(name=team_pk)
            )
        # if the user enters valid employee_pk and team_pk, yet they don't exist in the table
        if query_relation.first() is None:
            raise serializers.ValidationError('This relation does not exist.')
        
        # checking for the query params, to see what to update
        if 'work_arr' in request.data:
            if not isinstance(request.data['work_arr'], int):
                raise serializers.ValidationError('Please enter a valid work arrangement, an int.')
            # in which relations/teams is this employee
            # employee_relations = TERelation.objects.filter(employee=Employee.objects.filter(employee_id=employee_pk).first())
            # total_hours = 0
            # # this particular relation, since it's going to be counted twice in the for below
            # hours_prior_to_update = query_relation.first().work_arr 
            # for relation in employee_relations:
            #     total_hours += relation.work_arr

            # if total_hours + request.data['work_arr'] - hours_prior_to_update > total_work_arr:
            #     raise serializers.ValidationError(f'Employee {employee_pk} cannot work more than {total_work_arr} hours/week, you are exceeding by {total_hours + request.data["work_arr"] - hours_prior_to_update - total_work_arr}.')
            
            query_relation.update(work_arr=request.data['work_arr'])

        if 'employee_type' in request.data:
            if not isinstance(request.data['employee_type'], str):
                raise serializers.ValidationError('Please enter a valid employee type, a float', status=status.HTTP_404_NOT_FOUND)

            if request.data['employee_type'] not in ['EMPLOYEE', 'LEADER']:
                raise serializers.ValidationError('please enter a valid employee type', status=status.HTTP_404_NOT_FOUND)

            query_relation.update(employee_type=request.data['employee_type'])

        # employee_update and team_update have to be last, since they're used as identifiers  for the relation
        # if they're higher, a user can change the employee_id and previously mentioned params, and might cause an error
        if 'employee_update' in request.data:
            if not isinstance(request.data['employee_update'], str):
                raise serializers.ValidationError('Please enter a valid employee id, a string', status=status.HTTP_404_NOT_FOUND)
            # that the employee we're changing it with exists
            employee = Employee.objects.filter(employee_id=request.data['employee_update']).first()
            if employee is None:
                raise serializers.ValidationError('You are trying to replace the employee with non existing employee.', status=status.HTTP_404_NOT_FOUND)
            query_relation.update(employee=employee)
            
        if 'team_update' in request.data:
            if not isinstance(request.data['team_update'], str):
                raise serializers.ValidationError('Please enter a valid team name, a string', status=status.HTTP_404_NOT_FOUND)
            team = Team.objects.filter(team=request.data['team_update']).first()
            if team is None:
                raise serializers.ValidationError('You are trying to replace team with non existing team.', status=status.HTTP_404_NOT_FOUND)
            query_relation.update(team=team)            

        return Response(request.data, status=status.HTTP_204_NO_CONTENT)
        
    if request.method == 'DELETE':
        # identifying the query relation
        employee_pk = request.data['employee_pk']
        team_pk = request.data['team_pk']
        if employee_pk is None:
            raise serializers.ValidationError('Please provide an employee_pk.', status=status.HTTP_404_NOT_FOUND)
        if not isinstance(employee_pk, str):
            raise serializers.ValidationError('Please provide a valid employee_pk, a string.', status=status.HTTP_404_NOT_FOUND)
        if team_pk is None:
            raise serializers.ValidationError('Please provide a team_pk.', status=status.HTTP_404_NOT_FOUND)
        if not isinstance(team_pk, str):
            raise serializers.ValidationError('Please provide a valid team_pk, a string.', status=status.HTTP_404_NOT_FOUND)

        if not Employee.objects.filter(employee_id=employee_pk).exists():
            raise serializers.ValidationError(f'Employee with {employee_pk} does not exist.', status=status.HTTP_404_NOT_FOUND)
        if not Team.objects.filter(name=team_pk).exists():
            raise serializers.ValidationError(f'Team {team_pk} does not exist.', status=status.HTTP_404_NOT_FOUND)

        query_relation = qs.filter(
            employee=Employee.objects.get(employee_id=employee_pk),
            team=Team.objects.get(name=team_pk)
            )
        
        if query_relation.first() is None:
            raise serializers.ValidationError('This relation does not exist.', status=status.HTTP_404_NOT_FOUND)
        
        query_relation.delete()
        return Response({'message': f'Employee {employee_pk} in team {team_pk} deleted'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'message': 'invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        
# endregion


# region financials

@api_view(['GET'])
def financials_api(request):
    '''
        Given an employee_id and team (name) it'll return the employee's pay for their work in said team.
        If one of those params is given it'll give the total compensation for it, through all teams/employee.
        If none is given then it'll return the overall compensation for the whole company.
    '''

    query_employee = request.query_params.get('employee_id', None)
    query_team = request.query_params.get('team', None)
    qs = TERelation.objects.all()

    if query_employee is not None and query_team is not None:
        employee = Employee.objects.filter(employee_id=query_employee).first()
        team = Team.objects.filter(name=query_team).first()

        if employee is None:
            raise serializers.ValidationError('No employee with such id.', status=status.HTTP_404_NOT_FOUND)
        
        if team is None:
            raise serializers.ValidationError("No team with such name.")
        
        team_employee = qs.filter(employee=employee, team=team)
        if team_employee.first() is None:
            raise serializers.ValidationError('This employee is not assigned to this team.', status=status.HTTP_404_NOT_FOUND)

        serializer = PartialTeamEmployeeSerializer(instance=team_employee.first())
        pay = serializer.data['work_arr'] * employee.hourly_rate
        
        if serializer.data['employee_type'] == 'LEADER':
            pay *= 1.1

        return Response({"message": f'{employee} paid {pay} for his work in team {team}'})
    
    if query_employee is not None:
        employee = Employee.objects.filter(employee_id=query_employee).first()
        
        if employee is None:
            raise serializers.ValidationError('No employee with such id.', status=status.HTTP_404_NOT_FOUND)
        
        team_employees = qs.filter(employee=employee)
        if team_employees.first() is None:
            raise serializers.ValidationError('This employee is not assigned to any team.', status=status.HTTP_404_NOT_FOUND)

        serializer = PartialTeamEmployeeSerializer(instance=team_employees, many=True)

        hours_employee = 0
        hours_leader = 0
        for val in serializer.data:
            if val['employee_type'] == 'EMPLOYEE':
                hours_employee += val['work_arr']
            
            if val['employee_type'] == 'LEADER':
                hours_leader += val['work_arr']
        
        pay_employee = hours_employee * employee.hourly_rate
        pay_leader = hours_leader * employee.hourly_rate * 1.1

        return Response(f'Employee {employee} pay is {pay_employee} as employee, {pay_leader} as leader, total {pay_employee + pay_leader}', status=status.HTTP_200_OK)  

    if query_team is not None:
        team = Team.objects.filter(name=query_team).first()

        if team is None:
            raise serializers.ValidationError('No team with such name.', status=status.HTTP_404_NOT_FOUND)
        
        team_employees = qs.filter(team=team)
        if team_employees.first() is None:
            raise serializers.ValidationError('No employee is assigned to this team.', status=status.HTTP_404_NOT_FOUND)

        serializer = PartialTeamEmployeeSerializer(instance=team_employees, many=True)

        total_compensation = 0
        for val in serializer.data: 
            # in the data the employee will be given through their internal id
            employee = Employee.objects.filter(id=val['employee']).first()

            if val['employee_type'] == 'EMPLOYEE':
                total_compensation += employee.hourly_rate * val['work_arr']
            
            if val['employee_type'] == 'LEADER':
                total_compensation += employee.hourly_rate * val['work_arr'] * 1.1

        return Response({"message": serializer.data, "compensation": total_compensation})

    serializer = PartialTeamEmployeeSerializer(instance=qs, many=True)
    compensation = 0
    for val in serializer.data:
        compensation += Employee.objects.filter(id=val['employee']).first().hourly_rate * val['work_arr']

        if val['employee_type'] == 'LEADER':
            compensation *= 1.1

    return Response({"total compensation": compensation}, status=status.HTTP_200_OK)

# endregion