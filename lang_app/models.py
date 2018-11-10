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

    def give_answer(self, answer, score=False):
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
    def add_answer(self, question_pk, answer):
        qanda = QandA.objects.get(question__pk=question_pk)
        qanda.answer = answer
        # qanda.answer_correct = ...

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
        else:
            self.next_session.add_next_session(new_session)


class QandA(models.Model):
    '''
    this will represent one question and answer pair.
    This will just be a link from a specific question to an answer
    you might want to store the users actual answer.
    '''

    session = models.ForeignKey(Session, on_delete=None)
    question = models.ForeignKey(Card, on_delete=None)
    answer = models.CharField(max_length=1024, default=None)
    answer_correct = models.BooleanField()


class UserState(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_session = models.OneToOneField(Session, on_delete=models.CASCADE, default=None, null=True)

    def get_question(self, question_pk=None, answer=None):

        # If no question or answer was passed in, this is the first card
        # create the first session and add some questions
        if not self.current_session:
            new_session = Session.objects.create(user=self.user,
                                                 session_type='explore')
            new_session.save()
            total_cards = len(Card.objects.all())

            # Put sentences in the session
            for x in range(11):
                pk = randint(1, total_cards)
                qanda = QandA.objects.create(session=new_session,
                                             question=Card.objects.get(pk=pk))
                qanda.save()

            # Set the session
            self.current_session = new_session

        else:
            # If an answer was passed in then you need to add it to the qanda
            # and get the next question to return

            # check if you can still add answers to the session
            if not self.current_session.is_complete():
                self.current_session.add_answer(question_pk, answer)

            else:
                # if the session is complete then you need to move onto the next session
                if self.current_session.next_session:
                    # If there is a next session, just set that as the current session
                    self.current_session = self.current_session.next_session
                else:
                    # If there is no next session you need to create some.
                    # get the failed answers from the current session

                    for qanda in QandA.objects.filter(session=self.current_session, answer_correct=False):

                        # create the train session
                        train_session = Session.create(user=self.user,
                                                       session_type='train')
                        for q in qanda.question.similar_cards[:5]:
                            qanda = QandA.objects.create(session=train_session,
                                                         question=q)
                            qanda.save()

                        self.current_session.add_next_session(train_session)

                        # create the test session
                        test_session = Session.create(user=self.user,
                                                      session_type='test')
                        for q in qanda.question.similar_cards[5:10]:
                            qanda = QandA.objects.create(session=test_session,
                                                         question=q)
                            qanda.save()

                        self.current_session.add_next_session(test_session)

        return self.current_session.get_question()


























