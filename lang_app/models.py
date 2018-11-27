from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
# from utils.policies.Polices import PolicyOne, PolicyTwo, PolicyThree


class Sentence(models.Model):

    sentence = models.CharField(max_length=1024, unique=True)
    sentence_tree_string = models.CharField(max_length=1024, default=None)
    uncommon_words_score = models.IntegerField(default=0)

    def __str__(self):
        return self.sentence


class Question(models.Model):

    sentence = models.ForeignKey(Sentence, default=None, blank=True, related_name='questions', on_delete=models.CASCADE)
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

    @staticmethod
    def _format_tree_string(self, tree_string):
        # remove the newlines and whitespace that comes with tree string
        return "".join(tree_string.split())

    def __str__(self):
        s = "\nsentence: {}\n chunk: {}\n".format(self.sentence, self.chunk)
        return s


class QandA(models.Model):
    '''
    this will represent one question and answer pair.
    This will just be a link from a specific question to an answer
    you might want to store the users actual answer.
    '''

    class Meta:
        verbose_name = _("QandA")
        verbose_name_plural = _("QandAs")

    block = models.ForeignKey('Block', on_delete=models.CASCADE, null=True, related_name='qandas')
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True)
    answer = models.CharField(max_length=1024, default=None, null=True)
    answer_correct = models.BooleanField(null=True, default=None)
    qanda_type = models.CharField(max_length=1024, default='explore')

    def __str__(self):
        return "QandA for session: {}, question: {}..., answer: {}".format(self.block.pk,
                                                                           self.question.sentence.sentence[:25],
                                                                           self.answer)


class Block(models.Model):
    '''
    This will represent a block of questions and answers.
    This will have the type of the session, explore, train test
    It will also have a list of the qandq objects that are attached to it
    '''

    # user = models.ForeignKey(User, on_delete=None)
    # block_type = models.CharField(max_length=1024)
    # you could still keep this if you want to preserve the order between the blocks
    next_block = models.OneToOneField('Block', on_delete=models.SET_NULL, default=None, null=True)
    session = models.ForeignKey('Session', default=None, blank=True, null=True,
                                on_delete=models.CASCADE, related_name='blocks')

    @property
    def is_full(self):
        # Return true if there is no more space in the block for qandas
        return len(self.all_qandas) == self.session.block_size

    # Return true if all answers are complete
    @property
    def is_complete(self):
        return all([qanda.answer is not None for qanda in QandA.objects.filter(block=self)])

    @property
    def all_qandas(self):
        # Gets all the qandas for this session
        return QandA.objects.filter(block=self)

    # Add the answer to the question
    def add_answer(self, question_pk, answer, correct_bool):
        qanda = QandA.objects.get(question__pk=question_pk)
        qanda.answer = answer
        qanda.answer_correct = correct_bool
        qanda.save()

    # Return the first question you find that doesn't have an answer
    def get_question(self):
        for qanda in QandA.objects.filter(block=self):
            if qanda.answer is None:
                return qanda.question

    def add_next_block(self, new_block):
        # recursively add the session to the chain of sessions
        if not self.next_block:
            self.next_block = new_block
            self.save()
        else:
            self.next_block.add_next_block(new_block)

    def __str__(self):
        return "Block: {}, for Session: {}, Complete: {}".format(self.pk, self.session.pk, self.is_complete)


class Session(models.Model):

    user_state = models.ForeignKey('UserState', on_delete=None)
    current_block = models.OneToOneField(Block, default=None, blank=True, on_delete=models.SET_NULL,
                                         related_name='current_block', null=True)
    # This should keep track of which policy it was used with.
    policy_id = models.IntegerField(default=None)
    session_size = models.IntegerField(default=2)
    block_size = models.IntegerField(default=3)
    split = models.FloatField(default=0.5, null=True, blank=True)

    def increment_split(self, ratio):
        self.split += ratio
        # The split value should not go higher than one.
        if self.split > 1:
            self.split = 1
        self.save()
        return self.split

    @property
    def is_complete(self):
        return len(Block.objects.filter(session=self)) >= self.session_size and self.current_block.is_complete

    @property
    def all_qandas(self):
        # This is the history of all the quandas for this session
        return QandA.objects.filter(block__in=self.blocks.all())

    @property
    def passed_qandas(self):
        return self.all_qandas.filter(answer_correct=True)

    @property
    def failed_qandas(self):
        return self.all_qandas.filter(answer_correct=False)

    def __str__(self):
        return "Session for {} using Policy #{}".format(self.user_state.user, self.policy_id)


class UserState(models.Model):
    """
    This should also track the number of blocks in a session and be able to tell when the session
    is over. When that happens, the user should be told and the policy should switch
    over to the next one.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    current_policy_id = models.IntegerField(default=1, null=True, blank=True)
    policy_ids = models.CharField(max_length=1024, default="123")
    current_session = models.OneToOneField(Session, default=None, blank=True, on_delete=models.SET_NULL,
                                           related_name='current_session', null=True)

    @property
    def session_history(self):
        return self.current_session.all_qandas

    def create_session(self):
        self.switch_policy()
        self.current_session = Session.objects.create(user_state=self, policy_id=self.current_policy_id)
        self.save()
        return self.current_session

    def add_block(self, block):
        '''

        This is where you can track when new blocks are being added. When you reach ten, you will need to stop
        and show a message to the user and switch to the next policy

        There will be a different number of blocks for each policy as well. you need to bear that in mind
        '''

        if not self.current_session.current_block:
            self.current_session.current_block = block
            self.current_session.save()

        # Find out how many blocks are in this session already
        # if not self.current_session.is_complete:
        #     self.current_session.current_block.add_next_block(block)

        ''' YOU NEED TO FIX THIS, I'VE JUST LEFT IT HALF DONE'''

    def switch_policy(self):

        # If there is another policy id, move onto it
        if len(self.policy_ids) > 0:
            self.current_policy_id = int(self.policy_ids[0])
            self.policy_ids = self.policy_ids[1:]

            self.current_session = None
            self.save()

            return True
        else:
            return False

    def flush_state(self):
        '''
        Delete all user state for this user.
        :return: None
        '''

        # set the current session to null
        self.current_session = None
        self.current_policy_id = 1
        self.policy_ids = "123"
        self.save()

        # Delete all sessions
        user_state = UserState.objects.get(user=self.user)
        for session in Session.objects.filter(user_state=user_state):
            session.delete()

    def __str__(self):
        return "User State for {}".format(self.user)

