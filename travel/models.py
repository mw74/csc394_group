from django.db import models

# Create your models here.

    
class Travel(models.Model):
    destination = models.CharField(max_length=60)
    id = models.CharField(primary_key=True, max_length=3)
    #students = models.ManyToManyField(Student, related_name='student_courses')

    def __str__(self) -> str:
        return self.destination + "-" + self.number