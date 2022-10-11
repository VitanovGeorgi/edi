from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

total_work_arr = 48.0


class Employee(models.Model):
    """
    Employee model will be the most basic employee in the company
    """

    name = models.CharField(max_length=20)
    hourly_rate = models.FloatField()
    employee_id = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} {self.employee_id}"

    class Meta:
        ordering = ["employee_id"]


class Team(models.Model):
    """
    Team model contains only the name of the team, it needs to be unique for the purposes of this project,
    i.e. making it easier for HR
    """

    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class PartialTeamEmployeeRelation(models.Model):
    """
    PartialTeamEmployeeRelation will contain data for which employee is assigned to which team, with what
    work arrangement (weekly work hours) and with which role (must be either leader or employee, the former being
    unique per team)
    """

    employee = models.ForeignKey("Employee", on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.CASCADE)

    class Type(models.TextChoices):
        EMPLOYEE = "EMPLOYEE"
        LEADER = "LEADER"

    employee_type = models.CharField(
        max_length=20, choices=Type.choices, default=Type.EMPLOYEE
    )
    # just so someone doesn't put a negative work hours
    work_arr = models.PositiveIntegerField("Work Arrangements [hours/week]", default=40)

    def save(self, *args, **kwargs):
        # ensuring the user can't enter two leaders per team
        if (
            PartialTeamEmployeeRelation.objects.filter(  # that a leader already exists
                team=Team.objects.filter(name=self.team.name).first(),
                employee_type=self.Type.LEADER,
            ).exists()
            and self.employee_type == self.Type.LEADER
        ):  # and that the current input tries to make a second leader

            team_leader = PartialTeamEmployeeRelation.objects.filter(
                team=Team.objects.filter(name=self.team.name).first(),
                employee_type=self.Type.LEADER,
            ).first()
            raise ValidationError(f"Team already has a leader {team_leader.employee}")

        # ensuring that employees don't work more than total_work_arr in total
        qs = PartialTeamEmployeeRelation.objects.filter(employee=self.employee)
        if qs.exists():
            total_hours = 0  # hours saved so far
            for relation in qs:
                total_hours += relation.work_arr

            if total_hours + self.work_arr > total_work_arr:
                raise ValidationError(
                    f"Employee {self.employee} cannot work more than 48 hours/week,"
                    f" exceeding by {total_hours + self.work_arr - total_work_arr}"
                )

        return super(PartialTeamEmployeeRelation, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} {self.team} {self.work_arr}"

    class Meta:
        # only one employee can be in a team at once, and will also be used to identify the relation
        unique_together = ("employee", "team")
