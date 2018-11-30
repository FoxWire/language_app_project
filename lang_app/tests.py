import os
import sys
import django
sys.path.append('/home/stuart/PycharmProjects/workspaces/language_app_project')
os.environ['DJANGO_SETTINGS_MODULE'] = 'language_app_project.settings'
django.setup()

from django.test import TestCase
from utils.policies.policies import PolicyOne, PolicyTwo, PolicyThree
from utils.matrix_wrapper import MatrixWrapper
from lang_app.models import UserState, Session, QandA, Question, Block
from django.contrib.auth.models import User
from django.core.management import call_command
from random import choice


# class PolicyOneTests(TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         call_command('populatedb')
#
#     @classmethod
#     def tearDownClass(cls):
#         pass
#
#     def setUp(self):
#         self.user = User.objects.create(username='stuart')
#         self.user_state = UserState.objects.create(user=self.user)
#         self.policy = PolicyOne()
#
#     # -- Test the get_questions method --
#     def test_session_created_when_no_session(self):
#
#         self.policy.get_question(self.user_state)
#         new_session = self.user_state.current_session
#
#         self.assertIsNotNone(new_session)
#
#     def test_new_session_is_full_of_qandas(self):
#
#         self.policy.get_question(self.user_state)
#         new_session = self.user_state.current_session
#
#         self.assertTrue(new_session.current_block.is_full)
#
#     def test_no_new_session_created_when_one_exists(self):
#
#         self.policy.get_question(self.user_state)
#         num_sessions = len(Session.objects.all())
#         self.policy.get_question(self.user_state)
#
#         self.assertEqual(len(Session.objects.all()), num_sessions)
#
#     def test_question_is_returned(self):
#         qanda = self.policy.get_question(self.user_state)
#         t = type(Question.objects.all()[0])
#
#         self.assertIsNotNone(qanda)
#         self.assertEquals(type(qanda), t)
#
#     def test_question_returned_has_not_been_answered(self):
#         question = self.policy.get_question(self.user_state)
#         qanda = self.user_state.current_session.current_block.qandas.get(question=question)
#
#         self.assertIsNone(qanda.answer)
#
#     def test_get_random_returns_only_unseen_questions(self):
#         self.policy.get_question(self.user_state)  # This is just to create the session
#         random_question = self.policy.get_random(self.user_state)
#         questions_this_session = [qanda.question for qanda in self.user_state.current_session.all_qandas]
#
#         self.assertNotIn(random_question, questions_this_session)
#
#     # -- Tests for the update method --
#     def test_updates_answer(self):
#         question = self.policy.get_question(self.user_state)
#         self.policy.update_state(self.user_state, question.pk, question.chunk, True)
#         qanda = self.user_state.current_session.current_block.qandas.get(question=question)
#
#         self.assertTrue(qanda.answer_correct)
#         self.assertEquals(qanda.answer, question.chunk)
#
#     def test_new_block_not_created_when_session_complete(self):
#
#         self.policy.get_question(self.user_state)
#         session = self.user_state.current_session
#
#         while not session.is_complete:
#             block = Block.objects.create(session=session)
#             session.current_block = block
#             session.save()
#             while not block.is_full:
#                 question = choice(list(Question.objects.all()))
#                 QandA.objects.create(block=block, question=question, answer=question.chunk,
#                                      answer_correct=True, qanda_type='explore')
#
#         self.assertTrue(session.is_complete)
#         num_blocks = len(Block.objects.filter(session=session))
#         self.policy.get_question(self.user_state)
#         self.assertEquals(len(Block.objects.filter(session=session)), num_blocks)
#
#     # if the block is complete and the session not, it should create a new block
#     def test_creates_new_block_when_block_complete_and_session_incomplete(self):
#
#         # create session
#         question = self.policy.get_question(self.user_state)
#
#         # make the current block complete
#         for qanda in self.user_state.current_session.current_block.qandas.all():
#             qanda.answer = 'an answer'
#             qanda.save()
#
#         num_blocks = len(self.user_state.current_session.blocks.all())
#         self.assertTrue(self.user_state.current_session.current_block.is_complete)
#         self.assertFalse(self.user_state.current_session.is_complete)
#
#         self.policy.update_state(self.user_state, question.pk, '', True)
#         self.assertEquals(len(self.user_state.current_session.blocks.all()), num_blocks + 1)

#
# class PolicyTwoTests(TestCase):
#
#     @classmethod
#     def setUpClass(cls):
#         call_command('populatedb')
#
#     @classmethod
#     def tearDownClass(cls):
#         pass
#
#     def setUp(self):
#         self.user = User.objects.create(username='stuart')
#         self.user_state = UserState.objects.create(user=self.user)
#         self.user_state.flush_state()
#         self.policy = PolicyTwo()
#         self.matrix = MatrixWrapper()
#
#     # -- Tests for update state --
#     def test_updates_answer(self):
#
#         question = self.policy.get_question(self.user_state)
#         qanda = QandA.objects.get(question=question)
#         self.assertFalse(qanda.answer, 'answer')
#
#         self.policy.update_state(self.user_state, question.pk, 'answer', False)
#         qanda = QandA.objects.get(question=question)
#         self.assertTrue(qanda.answer, 'answer')
#
#     # check that a new block is not created when the session is complete
#     def test_new_block_not_created_when_session_complete(self):
#
#         self.policy.get_question(self.user_state)
#         session = self.user_state.current_session
#
#         while not session.is_complete:
#             block = Block.objects.create(session=session)
#             session.current_block = block
#             session.save()
#             while not block.is_full:
#                 question = choice(list(Question.objects.all()))
#                 QandA.objects.create(block=block, question=question, answer=question.chunk,
#                                      answer_correct=True, qanda_type='explore')
#
#         self.assertTrue(session.is_complete)
#         num_blocks = len(Block.objects.filter(session=session))
#         self.policy.get_question(self.user_state)
#         self.assertEquals(len(Block.objects.filter(session=session)), num_blocks)
#
#     def test_creates_new_block_when_block_complete_and_session_incomplete(self):
#
#         # create session
#         question = self.policy.get_question(self.user_state)
#
#         # make the current block complete
#         for qanda in self.user_state.current_session.current_block.qandas.all():
#             qanda.answer = 'an answer'
#             qanda.save()
#
#         num_blocks = len(self.user_state.current_session.blocks.all())
#         self.assertTrue(self.user_state.current_session.current_block.is_complete)
#         self.assertFalse(self.user_state.current_session.is_complete)
#
#         self.policy.update_state(self.user_state, question.pk, '', True)
#         self.assertEquals(len(self.user_state.current_session.blocks.all()), num_blocks + 1)
#
#     def test_questions_are_similar_to_previous_mistakes(self):
#
#         self.policy.get_question(self.user_state)
#
#         # make sure all questions in the initial block have been completed
#         pk = None
#         for qanda in QandA.objects.filter(block=self.user_state.current_session.current_block):
#             qanda.answer = 'an answer'
#             qanda.answer_correct = False
#             qanda.save()
#             pk = qanda.question.pk
#
#         self.assertTrue(self.user_state.current_session.current_block.is_complete)
#
#         # Get all the wrong questions from this block
#         wrong_questions = []
#         for qanda in QandA.objects.filter(block=self.user_state.current_session.current_block,
#                                           answer_correct=False):
#             wrong_questions.append(qanda.question)
#
#         # seen questions from previous block
#         seen_questions = [qanda.question for qanda in
#                           QandA.objects.filter(block__in=self.user_state.current_session.blocks.all())]
#
#         # Create a new block by updating
#         old_block = self.user_state.current_session.is_complete
#         self.policy.update_state(self.user_state, pk, 'an answer', False)
#         self.assertFalse(self.user_state.current_session.current_block.is_complete)
#
#         # test if the exploit questions are similar
#         most_similar_questions = []
#         for question in wrong_questions:
#             similar = self.matrix.get_similar_question_pks(question.pk)
#             for pk in similar:
#                 similar_q = Question.objects.get(pk=pk)
#                 if similar_q not in seen_questions and similar_q.sentence.sentence != question.sentence.sentence:
#                     most_similar_questions.append(similar_q)
#                     break
#
#         self.assertNotEqual(old_block, self.user_state.current_session.current_block)
#
#         # Get the questions from this block
#         new_questions = [qanda.question for qanda in QandA.objects.filter(block=self.user_state.current_session.current_block)]
#
#         for similar_question in most_similar_questions:
#             self.assertTrue(similar_question in new_questions)
#
#     def test_rest_of_block_filled_with_random(self):
#
#         # create the session
#         self.policy.get_question(self.user_state)
#
#         # make sure all questions in the initial block have been completed
#         q = None
#         for qanda in QandA.objects.filter(block=self.user_state.current_session.current_block):
#             qanda.answer = 'an answer'
#             qanda.answer_correct = False
#             qanda.save()
#             q = qanda
#
#         # Create a new block by updating, and set one answer to True
#         self.policy.update_state(self.user_state, q.question.pk, 'an answer', True)
#
#         # check that the new block has only one explore and two exploit
#         block_size = self.user_state.current_session.block_size
#         self.assertEquals(len(self.user_state.current_session.current_block.qandas.filter(qanda_type='exploit')), block_size - 1)
#         self.assertEquals(len(self.user_state.current_session.current_block.qandas.filter(qanda_type='explore')), 1)


class PolicyThreeTests(TestCase):

    '''
    The main things about this policy is that it uses a model to pick the next explore questions
    and the next exploit questions.
    The other thing is that it will adjust the ratio between the two depending on the right or
    wrong answers.
    '''

    @classmethod
    def setUpClass(cls):
        call_command('populatedb')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.user = User.objects.create(username='stuart')
        self.user_state = UserState.objects.create(user=self.user)
        self.user_state.flush_state()
        self.policy = PolicyThree()
        self.matrix = MatrixWrapper()

    # -- Tests for update state --
    def test_updates_answer(self):

        question = self.policy.get_question(self.user_state)
        qanda = QandA.objects.get(question=question)
        self.assertFalse(qanda.answer, 'answer')

        self.policy.update_state(self.user_state, question.pk, 'answer', False)
        qanda = QandA.objects.get(question=question)
        self.assertTrue(qanda.answer, 'answer')

    # check that a new block is not created when the session is complete
    def test_new_block_not_created_when_session_complete(self):

        self.policy.get_question(self.user_state)
        session = self.user_state.current_session

        while not session.is_complete:
            block = Block.objects.create(session=session)
            session.current_block = block
            session.save()
            while not block.is_full:
                question = choice(list(Question.objects.all()))
                QandA.objects.create(block=block, question=question, answer=question.chunk,
                                     answer_correct=True, qanda_type='explore')

        self.assertTrue(session.is_complete)
        num_blocks = len(Block.objects.filter(session=session))
        self.policy.get_question(self.user_state)
        self.assertEquals(len(Block.objects.filter(session=session)), num_blocks)

    def test_creates_new_block_when_block_complete_and_session_incomplete(self):

        # create session
        question = self.policy.get_question(self.user_state)

        # make the current block complete
        for qanda in self.user_state.current_session.current_block.qandas.all():
            qanda.answer = 'an answer'
            qanda.save()

        num_blocks = len(self.user_state.current_session.blocks.all())
        self.assertTrue(self.user_state.current_session.current_block.is_complete)
        self.assertFalse(self.user_state.current_session.is_complete)

        self.policy.update_state(self.user_state, question.pk, '', True)
        self.assertEquals(len(self.user_state.current_session.blocks.all()), num_blocks + 1)

    def test_model_uses_all_questions_asked_so_far(self):
        pass

    # test that the model is predicting something, you'll need to just set up some dummy data
    # get its prediction for three questions, then for the answer, find out how similar it
    # it is to the original. You can do this several times and get a score. You decide what the threshold is
    def test_prediction(self):

        # create the session
        question = self.policy.get_question(self.user_state)

        # Answer the questions wrong
        q = None
        wrong_qandas = []
        for qanda in QandA.objects.filter(block=self.user_state.current_session.current_block):
            qanda.answer_correct = False
            qanda.answer = 'a wrong answer'
            qanda.save()
            q = qanda.question.pk
            wrong_qandas.append(qanda)

        self.assertTrue(self.user_state.current_session.current_block.is_complete)

        # update the state to start a new block

        self.policy.update_state(self.user_state, q, 'an answer', False)

        self.assertFalse(self.user_state.current_session.current_block.is_complete)

        # Get the prediction for the next block
        for qanda in QandA.objects.filter(block=self.user_state.current_session.current_block, qanda_type='explore'):

            # Each of the new questions, should be sort of close to the each of the three wrongly answered ones.
            total_score = 0
            for wrong_qanda in wrong_qandas:
                total_score += self.matrix.get_value(qanda.question.pk, wrong_qanda.question.pk)
            print(total_score / 3)
            self.assertTrue((total_score / 3) < 40.0)


        # check that the prediction is sort of close to the original three




        pass




    # test how the model is being used for selecting practise questions too



    # make sure they get more exploit when they answer questions incorrectly

    # make sure they get more explore, when they answer questions correctly









    pass
















