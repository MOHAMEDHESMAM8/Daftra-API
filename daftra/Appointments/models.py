from django.db import models


class actions(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)


status = (
    ('scheduled', "scheduled"),
    ('done', "done"),
    ('dismissed', "dismissed")

)


class Appointments(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey("Users.Customers", on_delete=models.CASCADE, db_column="customer")
    date = models.DateField()
    time = models.TimeField()
    duration = models.TimeField()
    action = models.ForeignKey(actions, on_delete=models.CASCADE, db_column="action")
    notes = models.TextField(blank=True, null=True)
    employee = models.ForeignKey("Users.Employees", on_delete=models.CASCADE, db_column="employee",related_name= "appointment_employee")
    status = models.CharField(max_length=30, choices=status, default="scheduled")
    add_by = models.ForeignKey("Users.Employees", on_delete=models.CASCADE, db_column="add_by")
