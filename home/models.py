from django.db import models

class Home(models.Model):
    name = models.CharField(max_length =60)
    location = models.CharField(max_length = 60)
    interests = models.CharField(max_length = 200)
    time = models.CharField(max_length= 30)
    
    def __str__(self) -> str:
        return self.name