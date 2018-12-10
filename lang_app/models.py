from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
# from utils.policies.Polices import PolicyOne, PolicyTwo, PolicyThree
import re

verb_tags = {'MD', 'VB', 'VBD', 'VBG', 'VBN', 'VBP'}


class Sentence(models.Model):
    sentence = models.CharField(max_length=1024, unique=True)
    sentence_tree_string = models.CharField(max_length=1024, default=None)
    uncommon_words_score = models.IntegerField(default=0)

    @property
    def verbs(self):
        """
        Returns all the verb in the sentence
        :return: list
        """

        results = re.findall(r'\([A-Z]+ [A-Za-z\']+\)', self.sentence_tree_string)
        results = [result[1:-1].split(' ') for result in results]
        verbs = [result[1] for result in results if result[0] in verb_tags]
        return [verb.lower() for verb in verbs]

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

        """
        Returns the question data diveded into three parts, ready to be inserted into
        the html
        :return:dictionary
        """

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

    def give_answer(self, user_answer):
        user_answer = user_answer.strip().lower()
        chunk = self.chunk.strip().lower()

        regex = r'[^\w\s]'
        user_answer = re.sub(regex, '', user_answer)
        chunk = re.sub(regex, '', chunk)

        return user_answer == chunk, self.chunk.strip()

    @staticmethod
    def _format_tree_string(self, tree_string):
        """
        Removed the new lines and whitespaces that are in tree string
        :param self:
        :param tree_string:
        :return:
        """
        return "".join(tree_string.split())

    def __str__(self):
        s = "\nsentence: {}\n chunk: {}\n".format(self.sentence, self.chunk)
        return s


class QandA(models.Model):
    """
    Represents one question and answer pair
    """

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

    """
    Represents a block of questions and answers
    """
    next_block = models.OneToOneField('Block', on_delete=models.SET_NULL, default=None, null=True)
    session = models.ForeignKey('Session', default=None, blank=True, null=True,
                                on_delete=models.CASCADE, related_name='blocks')

    @property
    def is_full(self):
        """
        Return true if there is no more space left in the block for qanads
        :return:
        """
        return len(self.all_qandas) == self.session.block_size

    @property
    def is_complete(self):
        return all([qanda.answer is not None for qanda in QandA.objects.filter(block=self)])

    @property
    def all_qandas(self):
        """
        Returns all the qandas for this session
        :return:
        """
        return QandA.objects.filter(block=self)

    def add_answer(self, question_pk, answer, correct_bool):
        """
        Applies the answer passed in to the appropriate question in the block
        :param question_pk:
        :param answer:
        :param correct_bool:
        :return:
        """
        qanda = QandA.objects.get(question__pk=question_pk, block=self)
        qanda.answer = answer
        qanda.answer_correct = correct_bool
        qanda.save()

    def get_question(self):
        """
        Returns the first question in the block wihtout an answer
        :return:
        """
        for qanda in QandA.objects.filter(block=self):
            if qanda.answer is None:
                return qanda.question

    def add_next_block(self, new_block):
        if not self.next_block:
            self.next_block = new_block
            self.save()
        else:
            self.next_block.add_next_block(new_block)

    def __str__(self):
        return "Block: {}, for Session: {}, Complete: {}".format(self.pk, self.session.pk, self.is_complete)


class Session(models.Model):

    user_state = models.ForeignKey('UserState', on_delete=None, null=True, blank=True)
    current_block = models.OneToOneField(Block, default=None, blank=True, on_delete=models.SET_NULL,
                                         related_name='current_block', null=True)
    policy_id = models.IntegerField(default=None)
    session_size = models.IntegerField(default=6)
    block_size = models.IntegerField(default=6)
    split = models.FloatField(default=0.5, null=True, blank=True)

    def increment_split(self, ratio):
        self.split += ratio
        if self.split > 1:
            self.split = 1
        self.save()
        return self.split

    @property
    def is_complete(self):
        return len(Block.objects.filter(session=self)) >= self.session_size and self.current_block.is_complete

    @property
    def all_qandas(self):
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
    Represents the user in teh database.
    """

    user = models.OneToOneField(User, on_delete=None, null=True, blank=True)
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

        if not self.current_session.current_block:
            self.current_session.current_block = block
            self.current_session.save()

    def switch_policy(self):

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

