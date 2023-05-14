from django.core.management.base import BaseCommand
from subprocess import Popen
import os

class Command(BaseCommand):
    help = 'Starts the Celery worker along with the Django development server'

    def handle(self, *args, **options):
        cmd = f'celery -A homework worker --loglevel=info'
        Popen(cmd, shell=True, cwd=os.getcwd())
