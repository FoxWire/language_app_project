from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from lang_app.models import UserState


class Command(BaseCommand):

    help = '''
        Deletes the state of the user for the user name passed in as command line argument
        '''

    def add_arguments(self, parser):
        parser.add_argument('user_name', nargs='*', type=str)

    def handle(self, *args, **options):

        if not options['user_name']:
            print("*** Enter the name of the user to flush ***")
        else:
            # get the user that was passed in
            user = User.objects.get(username=options['user_name'][0])
            user_state = UserState.objects.get(user=user)
            user_state.flush_state()











