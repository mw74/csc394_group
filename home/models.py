from django.db import models
from django.contrib.auth.models import User, Group


def get_default_user():
    try:
        user = User.objects.get(username='default')
    except User.DoesNotExist:
        user = User.objects.create_user(username='default')
        regular_user_group = Group.objects.get(name='Regular User')
        user.groups.add(regular_user_group)
        user.is_staff = False
        user.is_superuser = False
        user.save()
    return user.id

class Home(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=get_default_user)
    name = models.CharField(max_length =60)
    location = models.CharField(max_length = 60)
    interests = models.CharField(max_length = 200)
    time = models.CharField(max_length= 30)
    responses = models.CharField(max_length=50000, default="N/A") #Stores Prompt/Response
    activity = models.CharField(max_length=60000, default="N/A") #stores response from travel_activities
    
    def __str__(self) -> str:
        return self.name +"/"+ str(self.user)
