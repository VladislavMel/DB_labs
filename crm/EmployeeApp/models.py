from django.db import models

# Create your models here.

class Task(models.Model):
    TaskId = models.AutoField(primary_key=True)
    TaskDescription = models.CharField(max_length=500)
    TaskStatus = models.CharField(max_length=500)
    TaskCreationDate = models.DateField()
    # FkEmployeeId = models.ForeignKey()

class Subtask(models.Model):
    SubtaskId = models.AutoField(primary_key=True)
    SubtaskDescription = models.CharField(max_length=500)
    SubtaskStatus = models.BooleanField()
    # FkTaskId = models.ForeignKey()