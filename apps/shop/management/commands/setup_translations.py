from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = 'Setup translation files for supported languages'

    def handle(self, *args, **options):
        self.stdout.write('Setting up translation files...')
        
        languages = ['es', 'fr', 'de', 'it']
        
        for lang in languages:
            os.system(f'django-admin makemessages -l {lang}')
            self.stdout.write(f'Created messages for {lang}')
        
        self.stdout.write(
            self.style.SUCCESS('Translation files created! Run "compilemessages" to compile them.')
        )
