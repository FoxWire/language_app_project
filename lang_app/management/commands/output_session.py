from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from lang_app.models import UserState, Session, Block, QandA
import json
from django.conf import settings
import os
import datetime


class Command(BaseCommand):

    help = '''
        Writes everything from a session to a json file
        '''

    def add_arguments(self, parser):
        parser.add_argument('session_id', nargs='*', type=str)

    def handle(self, *args, **options):

        if not options['session_id']:
            return

        session = Session.objects.get(pk=options['session_id'][0])
        user_name = session.user_state.user.username

        session_data = {
            'user_name': user_name,
            'session_complete_time': str(datetime.datetime.now()),
            'session_pk': session.pk,
            'session_size': session.session_size,
            'block_size': session.block_size,
            'policy_id': session.policy_id,
            'block_data': []
        }

        for block in Block.objects.filter(session=session):

            block_data = {
                'block_id': block.pk,
                'qanda_data': []
            }

            for qanda in QandA.objects.filter(block=block):
                qanda_data = {
                    'qanda_pk': qanda.pk,
                    'question_pk': qanda.question.pk,
                    'question': qanda.question.sentence.sentence,
                    'chunk': qanda.question.chunk,
                    'chunk_translation': qanda.question.chunk_translation,
                    'answer': qanda.answer,
                    'answer_correct': qanda.answer_correct,
                    'qanda_type': qanda.qanda_type,
                }
                block_data['qanda_data'].append(qanda_data)

            session_data['block_data'].append(block_data)

        path_to_dir = os.path.join(settings.BASE_DIR, 'data', 'session_data', user_name)
        if not os.path.exists(path_to_dir):
            os.makedirs(path_to_dir)

        path = os.path.join(path_to_dir, 'session_{}.json'.format(session.pk))
        with open(path, 'w') as file:
            json.dump(session_data, file, indent=4)









