from django.core.management.base import BaseCommand
from goals.utils import check_reminders

class Command(BaseCommand):
    help = 'Check for goals with upcoming reminders and create notifications'

    def handle(self, *args, **options):
        self.stdout.write('Checking for reminders...')
        check_reminders()
        self.stdout.write(self.style.SUCCESS('Successfully checked reminders')) 