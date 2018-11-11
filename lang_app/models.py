from django.db import models
from django.contrib.auth.models import User
from random import randint


class Sentence(models.Model):

    sentence = models.CharField(max_length=1024, unique=True)
    sentence_tree_string = models.CharField(max_length=1024, default=None)
    uncommon_words_score = models.IntegerField(default=0)

    def __str__(self):
        return self.sentence


class Card(models.Model):

    sentence = models.ForeignKey('Sentence', default=None, blank=True, related_name='cards', on_delete=models.CASCADE)
    chunk = models.CharField(max_length=1024)
    chunk_translation = models.CharField(max_length=1024)
    chunk_tree_string = models.CharField(max_length=1024)
    similar_cards = models.CharField(max_length=128, default=None, null=True)
    question_tree_string = models.CharField(max_length=1024, default=None, null=True)

    def ask_question(self):

        # sentence = self.sentence.sentence
        # close_deletion = sentence.replace(self.chunk, '_' * len(self.chunk))
        # spaces = ' ' * (len(close_deletion.split("_")[0].strip()) - 1)
        # question = "{}\n{}<{}>".format(close_deletion, spaces, self.chunk_translation)

        # In order to use the question in the html, we need to sentence, split on the chunk
        # we will return both parts and the chunk

        sentence = self.sentence.sentence
        data = {'b': self.chunk_translation}

        if sentence.startswith(self.chunk):
            data['a'] = None
            data['c'] = sentence.replace(self.chunk, '')
        elif sentence.endswith(self.chunk):
            data['a'] = sentence.replace(self.chunk, '')
            data['c'] = None
        else:
            parts = sentence.split(self.chunk)
            data['a'] = parts[0]
            data['c'] = parts[1]

        return data

    def give_answer(self, answer):
        return answer.strip().lower() == self.chunk.strip().lower(), self.chunk.strip()

    def _format_tree_string(self, tree_string):
        # remove the newlines and whitespace that comes with tree string
        return "".join(tree_string.split())

    def __str__(self):
        s = "\nsentence: {}\n chunk: {}\n".format(self.sentence, self.chunk)
        return s


class Session(models.Model):
    '''
    This will represent a block of questions and answers.
    This will have the type of the session, explore, train test
    It will also have a list of the qandq objects that are attached to it
    '''

    user = models.ForeignKey(User, on_delete=None)
    session_type = models.CharField(max_length=1024)
    next_session = models.ForeignKey('Session', on_delete=None, default=None, null=True)

    # Add the answer to the question
    def add_answer(self, question_pk, answer, correct_bool):
        qanda = QandA.objects.get(question__pk=question_pk)
        qanda.answer = answer
        qanda.answer_correct = correct_bool
        qanda.save()

    # Return the first question you find that doesn't have an answer
    def get_question(self):
        for qanda in QandA.objects.filter(session=self):
            if qanda.answer is None:
                return qanda.question

    # Return true if all answers are complete
    def is_complete(self):
        return [qanda.answer for qanda in QandA.objects.filter(session=self)].count(None) == 0

    def add_next_session(self, new_session):
        # recursively add the session to the chain of sessions
        if not self.next_session:
            self.next_session = new_session
            self.save()
        else:
            self.next_session.add_next_session(new_session)


class QandA(models.Model):
    '''
    this will represent one question and answer pair.
    This will just be a link from a specific question to an answer
    you might want to store the users actual answer.
    '''

    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    question = models.ForeignKey(Card, on_delete=None)
    answer = models.CharField(max_length=1024, default=None, null=True)
    answer_correct = models.BooleanField(null=True, default=None)

    def __str__(self):
        return "QandA for session: {}, question: {}..., answer: {}".format(self.session.pk, self.question.sentence.sentence[:25], self.answer)


class UserState(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_session = models.OneToOneField(Session, on_delete=None, default=None, null=True, blank=True)
    session_size = models.IntegerField(default=3)

    def get_question(self):
        '''
        Returns the next question. If there is no next session (as is the case
        with the first question), create the initial session first
        :return:
        '''

        if not self.current_session:
            print("here lksjd flks jlkjlk jk")
            new_session = Session.objects.create(user=self.user,
                                                 session_type='explore')
            # new_session.save()
            total_cards = len(Card.objects.all())

            # Put sentences in the session
            for x in range(self.session_size):
                pk = randint(1, total_cards)
                qanda = QandA.objects.create(session=new_session,
                                             question=Card.objects.get(pk=pk))
                # qanda.save()

            # Set the session
            self.current_session = new_session
            self.save()

        return self.current_session.get_question()

    def update_state(self, question_pk, answer, correct_bool):
        '''

        :param question_pk:
        :param answer:
        :return:
        '''

        # If the current session is not complete, add the answer to the current question
        if not self.current_session.is_complete():
            self.current_session.add_answer(question_pk, answer, correct_bool)

        # If the session is complete then you need to move onto the next session
        if self.current_session.is_complete():
            # If there is a next session, set that to the current session
            if self.current_session.next_session:
                self.current_session = self.current_session.next_session
                self.save()

            # If there is no next session you need to create some.
            else:
                # Iterate over the failed questions from the current session, creating sessions and questions
                for qanda in QandA.objects.filter(session=self.current_session, answer_correct=False):

                    # create the train session
                    train_session = Session.objects.create(user=self.user,
                                                           session_type='train')
                    for q in qanda.question.similar_cards[:self.session_size]:
                        QandA.objects.create(session=train_session,
                                             question=q)

                    self.current_session.add_next_session(train_session)

                    # create the test session
                    test_session = Session.objects.create(user=self.user,
                                                          session_type='test')
                    for q in qanda.question.similar_cards[self.session_size:self.session_size * 2]:
                        QandA.objects.create(session=test_session,
                                             question=q)

                    self.current_session.add_next_session(test_session)
                    self.save()

    def flush_state(self):
        '''
        Delete all user state for this user.
        :return: None
        '''

        # set the current session to null
        self.current_session = None
        self.save()

        # Delete all sessions
        for session in Session.objects.filter(user=self.user):
            session.delete()

    def __str__(self):
        return "User State Object for {}".format(self.user)


























