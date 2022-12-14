from django.test import TestCase
from ..models import Employee, Team, PartialTeamEmployeeRelation
from django.core.exceptions import ValidationError


class TeamModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.team = Team.objects.create(name="Trial team")

    # checking the name of the team is equal to the output of the string here
    def test_model_str(self):
        self.assertEqual(
            str(self.team.name), "Trial team"
        )  # calling str() since the dunder method in Team3 is str


class EmployeeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # team.save()
        cls.employee = Employee.objects.create(
            name="George", hourly_rate=12, employee_id="A123"
        )

    # checking the name of the team is equal to the output of the string here
    def test_model_str(self):
        self.assertEqual(
            f"{self.employee.name} {self.employee.employee_id}", "George A123"
        )


class PartialModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.team = Team.objects.create(name="Test_team")
        # team.save()
        employee = Employee.objects.create(
            name="George", hourly_rate=12, employee_id="A123"
        )
        # employee.save()
        cls.team_employee_relation = PartialTeamEmployeeRelation.objects.create(
            employee=employee, team=cls.team, employee_type="LEADER", work_arr=20.0
        )

    def test_model_str(self):
        self.assertEqual(
            f"{str(self.team_employee_relation.employee)} {str(self.team_employee_relation.team)}"
            f" {self.team_employee_relation.work_arr}",
            "George A123 Test_team 20.0",
        )

    def test_work_arr(self):
        with self.assertRaises(ValidationError):
            relation = PartialTeamEmployeeRelation.objects.create(
                employee=self.team_employee_relation.employee,
                team=self.team_employee_relation.team,
                employee_type="EMPLOYEE",
                work_arr=120.0,
            )

    def test_two_leaders(self):
        with self.assertRaises(ValidationError):
            employee = Employee.objects.create(
                name="Aleksandar", hourly_rate=15, employee_id="C123"
            )
            relation = PartialTeamEmployeeRelation.objects.create(
                employee=employee,
                team=self.team,
                employee_type="LEADER",
                work_arr=40,
            )
