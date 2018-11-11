import os
from django.core.management.base import BaseCommand
from language_app_project.settings import BASE_DIR


class Command(BaseCommand):
    help = "Combination of commands to delete and rebuild the database."

    def handle(self, *args, **options):

        print('*** Deleting database... ***')
        db = os.path.join(BASE_DIR, 'db.sqlite3')
        os.system("rm " + db)

        print("*** Deleting migrations... ***")
        migrations = os.path.join(BASE_DIR, 'lang_app/migrations/000*')
        os.system("rm " + migrations)

        print("*** Recreating database... ***")
        os.system("python manage.py migrate")

        print("*** Making migrations... ***")
        os.system("python manage.py makemigrations")

        print("*** Applying migrations... ***")
        os.system("python manage.py migrate")

        print("*** Populating the database... ***")
        os.system("python manage.py populate_db")

