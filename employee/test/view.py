from ..models import Employee, Team, PartialTeamEmployeeRelation
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class EmployeeApiTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.employee1 = Employee.objects.create(
            name="Employee1", hourly_rate=12, employee_id="A123"
        )
        cls.employee2 = Employee.objects.create(
            name="Employee2", hourly_rate=13, employee_id="B123"
        )
        cls.url = reverse("employee-api")

    def test_get_api(self):
        response = self.client.get(self.url, format="json")
        # to send query params
        response_with_query = self.client.get(
            self.url, {"employee_id": "A123"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data,
            [
                {"name": "Employee1", "hourly_rate": 12, "employee_id": "A123"},
                {"name": "Employee2", "hourly_rate": 13, "employee_id": "B123"},
            ],
        )
        self.assertEqual(response_with_query.status_code, status.HTTP_200_OK)
        # have to put it in [], since len({"name",,}) counts the k-v pairs in it
        self.assertEqual(len([response_with_query.data]), 1)
        self.assertEqual(
            response_with_query.data,
            {"name": "Employee1", "hourly_rate": 12, "employee_id": "A123"},
        )

    def test_post_api(self):
        # this employee is created here, in this db
        employee = {"name": "Employee", "hourly_rate": 14, "employee_id": "C123"}
        response = self.client.post(self.url, employee, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # check whether if it's of type Employee, thus knowing it's saved correctly
        # self.assertTrue(isinstance(employee, Employee))
        self.assertEqual(len([response.data]), 1)  # it'll return a QuerySet of length 1
        self.assertEqual(Employee.objects.all().count(), 3)
        self.assertEqual(
            Employee.objects.filter(name=employee["name"]).first().name, "Employee"
        )
        self.assertEqual(
            Employee.objects.filter(hourly_rate=employee["hourly_rate"])
            .first()
            .hourly_rate,
            14,
        )
        self.assertEqual(
            Employee.objects.filter(employee_id=employee["employee_id"])
            .first()
            .employee_id,
            "C123",
        )

    def test_put_api(self):
        response_name = self.client.put(
            "/api/employee/A123", {"name": "Employee4"}, format="json"
        )
        self.assertEqual(response_name.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Employee.objects.all().count(), 2)
        self.assertEqual(
            Employee.objects.filter(id=self.employee1.id).first().name, "Employee4"
        )

        response_hourly_rate = self.client.put(
            "/api/employee/A123", {"hourly_rate": 15.0}, format="json"
        )
        self.assertEqual(response_hourly_rate.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Employee.objects.all().count(), 2)
        self.assertEqual(
            Employee.objects.filter(id=self.employee1.id).first().hourly_rate, 15.0
        )

        response_employee_id = self.client.put(
            "/api/employee/A123", {"employee_id": "D123"}, format="json"
        )
        self.assertEqual(response_employee_id.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Employee.objects.all().count(), 2)
        self.assertEqual(
            Employee.objects.filter(id=self.employee1.id).first().employee_id, "D123"
        )

    def test_delete_api(self):
        # to actually send url/pk
        response = self.client.delete("/api/employee/B123", format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Employee.objects.all().count(), 1)
        self.assertEqual(
            Employee.objects.filter(id=self.employee1.id).first().name, "Employee1"
        )
        self.assertEqual(
            Employee.objects.filter(id=self.employee1.id).first().hourly_rate, 12
        )
        self.assertEqual(
            Employee.objects.filter(id=self.employee1.id).first().employee_id, "A123"
        )


class TeamApiTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.team1 = Team.objects.create(name="Team1")
        cls.team2 = Team.objects.create(name="Team2")
        cls.url = reverse("team-api")

    def test_get_api(self):
        response = self.client.get(self.url, format="json")
        response_name = self.client.get(self.url, {"name": "Team1"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data, [{"name": "Team1"}, {"name": "Team2"}])
        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len([response_name.data]), 1)
        self.assertEqual(response_name.data, {"name": "Team1"})

    def test_post_api(self):
        team = {"name": "Team"}
        response = self.client.post(self.url, team, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Team.objects.all().count(), 3)
        self.assertEqual(Team.objects.filter(name=team["name"]).first().name, "Team")

    def test_put_api(self):
        response = self.client.put("/api/team/Team1", {"name": "Team4"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Team.objects.all().count(), 2)
        self.assertEqual(Team.objects.filter(id=self.team1.id).first().name, "Team4")

    def test_delete_api(self):
        response = self.client.delete("/api/team/Team2", format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Team.objects.all().count(), 1)
        self.assertEqual(Team.objects.filter(id=self.team1.id).first().name, "Team1")


class PartialTeamEmployeeApiTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.employee1 = Employee.objects.create(
            name="Employee1", hourly_rate=12, employee_id="A123"
        )
        cls.employee2 = Employee.objects.create(
            name="Employee2", hourly_rate=13, employee_id="B123"
        )
        cls.team1 = Team.objects.create(name="Team1")
        cls.team2 = Team.objects.create(name="Team2")

        cls.e1t1 = PartialTeamEmployeeRelation.objects.create(
            employee=cls.employee1, team=cls.team1, employee_type="LEADER", work_arr=24
        )
        cls.e1t2 = PartialTeamEmployeeRelation.objects.create(
            employee=cls.employee1,
            team=cls.team2,
            employee_type="EMPLOYEE",
            work_arr=16,
        )
        cls.e2t1 = PartialTeamEmployeeRelation.objects.create(
            employee=cls.employee2,
            team=cls.team1,
            employee_type="EMPLOYEE",
            work_arr=18,
        )
        cls.e2t2 = PartialTeamEmployeeRelation.objects.create(
            employee=cls.employee2, team=cls.team2, employee_type="LEADER", work_arr=30
        )
        cls.url = reverse("team-employee-api")

    def test_get_api(self):
        response = self.client.get(self.url, format="json")
        response_name = self.client.get(
            self.url, {"employee_id": "A123"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

        self.assertEqual(
            response.data,
            [
                {
                    "employee_type": "LEADER",
                    "work_arr": 24,
                    "employee": "A123",
                    "team": "Team1",
                },
                {
                    "employee_type": "EMPLOYEE",
                    "work_arr": 16,
                    "employee": "A123",
                    "team": "Team2",
                },
                {
                    "employee_type": "EMPLOYEE",
                    "work_arr": 18,
                    "employee": "B123",
                    "team": "Team1",
                },
                {
                    "employee_type": "LEADER",
                    "work_arr": 30,
                    "employee": "B123",
                    "team": "Team2",
                },
            ],
        )
        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_name.data), 2)
        self.assertEqual(
            response_name.data,
            [
                {
                    "employee_type": "LEADER",
                    "work_arr": 24,
                    "employee": "A123",
                    "team": "Team1",
                },
                {
                    "employee_type": "EMPLOYEE",
                    "work_arr": 16,
                    "employee": "A123",
                    "team": "Team2",
                },
            ],
        )

    def test_post_api(self):
        employee = Employee.objects.create(
            name="Employee", hourly_rate=14, employee_id="C123"
        )
        # Employee.save() # so we have them actually, in the post we'll just send a json of the relation, not the employee/team itself
        team = Team.objects.create(name="Team")
        # Team.save()
        e3t3 = {
            "employee_type": "LEADER",
            "work_arr": 20.0,
            "employee": "C123",
            "team": "Team",
        }
        e3t1 = {
            "employee_type": "EMPLOYEE",
            "work_arr": 20.0,
            "employee": "C123",
            "team": "Team1",
        }

        response_1 = self.client.post(self.url, e3t1, format="json")
        response_3 = self.client.post(self.url, e3t3, format="json")

        self.assertEqual(PartialTeamEmployeeRelation.objects.all().count(), 6)

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len([response_1.data]), 1)
        self.assertEqual(
            PartialTeamEmployeeRelation.objects.filter(
                employee=employee.id, team=self.team1.id
            )
            .first()
            .employee.employee_id,
            e3t1["employee"],
        )
        self.assertEqual(
            PartialTeamEmployeeRelation.objects.filter(
                employee=employee.id, team=self.team1.id
            )
            .first()
            .employee_type,
            e3t1["employee_type"],
        )
        self.assertEqual(
            PartialTeamEmployeeRelation.objects.filter(
                employee=employee.id, team=self.team1.id
            )
            .first()
            .team.name,
            e3t1["team"],
        )
        self.assertEqual(
            PartialTeamEmployeeRelation.objects.filter(
                employee=employee.id, team=self.team1.id
            )
            .first()
            .work_arr,
            e3t1["work_arr"],
        )

        self.assertEqual(response_3.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len([response_3.data]), 1)
        # PartialTeamEmployeeRelation has employee and team with internal id
        self.assertEqual(
            PartialTeamEmployeeRelation.objects.filter(
                employee=employee.id, team=team.id
            )
            .first()
            .employee.employee_id,
            e3t3["employee"],
        )
        self.assertEqual(
            PartialTeamEmployeeRelation.objects.filter(
                employee=employee.id, team=team.id
            )
            .first()
            .employee_type,
            e3t3["employee_type"],
        )
        self.assertEqual(
            PartialTeamEmployeeRelation.objects.filter(
                employee=employee.id, team=team.id
            )
            .first()
            .team.name,
            e3t3["team"],
        )
        self.assertEqual(
            PartialTeamEmployeeRelation.objects.filter(
                employee=employee.id, team=team.id
            )
            .first()
            .work_arr,
            e3t3["work_arr"],
        )

    def test_put_api(self):
        response_employee = self.client.put(
            self.url,
            {"employee_pk": "A123", "team_pk": "Team1", "employee_type": "EMPLOYEE"},
            format="json",
        )
        self.assertEqual(response_employee.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PartialTeamEmployeeRelation.objects.all().count(), 4)
        self.assertEqual(
            PartialTeamEmployeeRelation.objects.filter(
                employee=self.employee1.id, team=self.team1.id
            )
            .first()
            .employee_type,
            "EMPLOYEE",
        )

        response_arr = self.client.put(
            self.url,
            {"employee_pk": "A123", "team_pk": "Team1", "work_arr": 5},
            format="json",
        )
        self.assertEqual(response_employee.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PartialTeamEmployeeRelation.objects.all().count(), 4)
        self.assertEqual(
            PartialTeamEmployeeRelation.objects.filter(
                employee=self.employee1.id, team=self.team1.id
            )
            .first()
            .work_arr,
            5,
        )

    def test_delete_api(self):
        response = self.client.delete(
            self.url, {"employee_pk": "B123", "team_pk": "Team2"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PartialTeamEmployeeRelation.objects.all().count(), 3)

        self.assertEqual(
            PartialTeamEmployeeRelation.objects.filter(
                employee=self.employee1.id, team=self.team1.id
            ).first(),
            self.e1t1,
        )

        self.assertEqual(
            PartialTeamEmployeeRelation.objects.filter(
                employee=self.employee1.id, team=self.team2.id
            ).first(),
            self.e1t2,
        )

        self.assertEqual(
            PartialTeamEmployeeRelation.objects.filter(
                employee=self.employee2.id, team=self.team1.id
            ).first(),
            self.e2t1,
        )


class FinancialsApiTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.employee1 = Employee.objects.create(
            name="Employee1", hourly_rate=12, employee_id="A123"
        )
        cls.employee2 = Employee.objects.create(
            name="Employee2", hourly_rate=13, employee_id="B123"
        )
        cls.team1 = Team.objects.create(name="Team1")
        cls.team2 = Team.objects.create(name="Team2")

        cls.e1t1 = PartialTeamEmployeeRelation.objects.create(
            employee=cls.employee1, team=cls.team1, employee_type="LEADER", work_arr=24
        )
        cls.e1t2 = PartialTeamEmployeeRelation.objects.create(
            employee=cls.employee1,
            team=cls.team2,
            employee_type="EMPLOYEE",
            work_arr=16,
        )
        cls.e2t1 = PartialTeamEmployeeRelation.objects.create(
            employee=cls.employee2,
            team=cls.team1,
            employee_type="EMPLOYEE",
            work_arr=16,
        )
        cls.e2t2 = PartialTeamEmployeeRelation.objects.create(
            employee=cls.employee2, team=cls.team2, employee_type="LEADER", work_arr=32
        )
        cls.url = reverse("financials-api")

    def test_get_api(self):
        # for the values, I ran the test and saw the results, or just calculate them by hand, keeping in mind they're floats
        response = self.client.get(self.url, format="json")
        response_employee = self.client.get(
            self.url, {"employee_id": "A123"}, format="json"
        )
        response_team = self.client.get(self.url, {"team": "Team1"}, format="json")
        response_employee_team = self.client.get(
            self.url, {"employee_id": "A123", "team": "Team1"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, {"total compensation": 1246.0800000000002})

        self.assertEqual(response_employee.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response_employee.data,
            f"Employee Employee1 A123 pay is 192.0 as employee, 316.8 as leader, total 508.8",
        )

        self.assertEqual(response_team.status_code, status.HTTP_200_OK)
        self.assertEqual(response_team.data, {"compensation": 524.8})

        self.assertEqual(response_employee_team.status_code, status.HTTP_200_OK)
