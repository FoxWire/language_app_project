from lang_app.models import Question, QandA, Session, Block, UserState
from utils.matrix_wrapper import MatrixWrapper
from random import choice, randint, shuffle
from math import ceil

matrix = MatrixWrapper()


# Just returns some random pks, for testing
class DummyMatrix:

    def get_similar_question_pks(self, pk):
        pks = [q.pk for q in Question.objects.all()]
        shuffle(pks)
        return pks


# matrix = DummyMatrix()


# Abstract class
class Policy:

    def get_question(self, user_state):

        """
        If the user is asking for the first question, there will be no session or block and so
        these are created here. The initial block is populated with random questions and one is returned.
        Otherwise the next question from the current block is returned.
        This behaviour is common to each of the three policies.
        :param user_state:
        :return: Question
        """

        if not user_state.current_session:

            # Create the new session
            new_session = user_state.create_session()
            # Create the new block for the session
            new_block = Block.objects.create(session=new_session)

            # Fill up the new block with random qandas
            while not new_block.is_full:
                QandA.objects.create(question=self.get_random(user_state), block=new_block)

            # Add the new block
            user_state.add_block(new_block)

        return user_state.current_session.current_block.get_question()

    def update_state(self, user_state, question_pk, answer, correct_bool): pass

    @staticmethod
    def get_random(user_state, exclude_pks=None):
        """
        Gets a random question that hasn't been seen in the current session.
        Optional exclude can be used to further questions to be excluded
        :param user_state:
        :param exclude:
        :return:
        """
        if user_state.current_session:
            seen_pks = [qanda.question.pk for qanda in user_state.session_history]
            seen_pks = seen_pks + exclude_pks if exclude_pks else seen_pks
            qs = Question.objects.exclude(pk__in=seen_pks)
        else:
            qs = Question.objects.all()
        return choice(list(qs))


class PolicyOne(Policy):

    """
    This policy will just create a block of random questions each time. There is no practise or exploration
    and the previous answers are not taken into account in any way.
    """

    def update_state(self, user_state, question_pk, answer, correct_bool):

        # Update with the answer from the user
        user_state.current_session.current_block.add_answer(question_pk, answer, correct_bool)

        if user_state.current_session.current_block.is_complete and not user_state.current_session.is_complete:

            # Create a new block ...
            new_block = Block.objects.create(session=user_state.current_session)

            # Fill up the new block with random qandas
            while not new_block.is_full:
                QandA.objects.create(question=self.get_random(user_state), block=new_block, qanda_type='explore')

                user_state.current_session.current_block = new_block
                user_state.current_session.save()


class PolicyTwo(Policy):
    """
    After the initial block of random questions, this policy will fill the next block with
    similar questions to ones that were previously failed (answered wrongly). It will attempt
    to fill the block with as many of these as possible and add random questions if there are
    not enough.

    For each block, it will consider all of the failed questions for the session so far.
    """

    def update_state(self, user_state, question_pk, answer, correct_bool):
        '''
        When you are creating a new block, you look at all the questions that they have failed in this session
        you find the next most similar question for each that hasn't already been asked and doesn't have the same sentence
        as the one that they have just seen and fill the next block up with these. if you have any space left in the
        block, you just fill it up with random ones

        Note: you might not want to exclude all the sentences that they have seen already, you don't really have
        enough questions for that. You only remove the same sentences as they have just seen.
        but that means I have to keep track of the questions in different blocks
        '''

        # Update with the answer from the user
        user_state.current_session.current_block.add_answer(question_pk, answer, correct_bool)

        if user_state.current_session.current_block.is_complete and not user_state.current_session.is_complete:

            # Create a new block
            new_block = Block.objects.create(session=user_state.current_session)

            # Get a list of all the questions that have been seen already
            seen_questions = [qanda.question for qanda in user_state.session_history]

            for failed_qanda in user_state.current_session.failed_qandas:

                # For each of the failed qandas, find the next most similar question that doesn't have the same
                # sentence and hasn't been see already. The default is a random question
                next_question = self.get_random(user_state)
                for pk in matrix.get_similar_question_pks(failed_qanda.question.pk):
                    question = Question.objects.get(pk=pk)

                    if question.sentence != failed_qanda.question.sentence and question not in seen_questions:
                        next_question = question
                        seen_questions.append(next_question)
                        break

                '''
                I don't know if I should shuffle the list of canditate questions here. At the moment, it will 
                just find the next most similar cards to the same ones that you got wrong at the start. 
                
                OR do you want it to only look at the wrong questions from the previous block? and fill up the rest with 
                randoms?
                '''

                # If there is space in the block, add the new quanda
                if not new_block.is_full:
                    QandA.objects.create(question=next_question, block=new_block, qanda_type='exploit')
                else:
                    break

            # If the block is not yet filled up, add some more random questions
            while not new_block.is_full:
                QandA.objects.create(question=self.get_random(user_state), block=new_block, qanda_type='explore')

            user_state.current_session.current_block = new_block
            user_state.current_session.save()


class PolicyThree(Policy):
    
    """
    After the initial set of random questions, this policy will attempt to find the most difficult
    questions based on all of the answers given so far.
    Each block will consist of an explore and exploit phase and the focus will shift from
    more explore to more exploit over the course of the session.

    Rejig: after the initial set of random questions, this policy will look at all the questions that you have got wrong so
    far in this session and find the next most similar one that hasn't already been asked and doesn't have the same sentence to
    the one that was failed. It will fill up the block based on that and then fill the rest up with random questions
    The ratio will be determined by the number of right and wrong answers in the previous block. If they got more right, then
    we'll let them explore some more before exploiting.


    """
    def update_state(self, user_state, question_pk, answer, correct_bool):
        '''
        This first updates with the answer that was passed in
        Then checks if the block is complete
        If it is, it moves onto the next block if there is one
        Otherwise, it will create two more blocks
        '''

        # There will always be an answer passed in here. Update the answer
        user_state.current_session.current_block.add_answer(question_pk, answer, correct_bool)

        # Check if the current block is now complete after having added the answer
        if user_state.current_session.current_block.is_complete and not user_state.current_session.is_complete:

            # Get the failed questions so far
            failed_qandas = [q for q in user_state.current_session.failed_qandas]

            # Get a list of the questions that have been seen already
            seen_questions = [qanda.question for qanda in user_state.session_history]
            shuffle(failed_qandas)

            # Set default values for the number of explore and exploit questions in next block
            exploit_size = 0
            explore_size = user_state.current_session.block_size

            # If they have previously failed some questions, adjust the ratios
            if failed_qandas:

                # Get the previous exploit questions for the current (completed) block
                exploit_previous = user_state.current_session.current_block.all_qandas.filter(qanda_type='exploit')
                exploit_previous_correct = exploit_previous.filter(answer_correct=True)

                # If they get them all right, increase by 0.15, one wrong, 0.1 everything else 0.05
                difference = abs(len(exploit_previous) - len(exploit_previous_correct))
                split_val = 0.05
                values = {0: 0.15, 1: 0.1}
                if difference in values:
                    split_val = values[difference]
                split = user_state.current_session.increment_split(split_val)

                # The ratio between explore and exploit in the block
                explore_size = ceil(user_state.current_session.block_size * split)
                exploit_size = user_state.current_session.block_size - explore_size

            # make the block
            new_block = Block.objects.create(session=user_state.current_session)

            exploit_questions, explore_questions = [], []

            # If you don't get enough in the first run here, it will just keep iterating over the failed questions
            # because the new ones are added to the seen questions, they won't be repeated lots of times.
            while len(exploit_questions) < exploit_size:

                next_question = None

                # Find the next question
                for failed_qanda in failed_qandas:

                    # For each of the failed qandas, find the next question and add it to the list
                    for pk in matrix.get_similar_question_pks(failed_qanda.question.pk):
                        question = Question.objects.get(pk=pk)

                        if question.sentence != failed_qanda.question.sentence and question not in seen_questions:
                            next_question = question
                            break
                    break

                exploit_questions.append(next_question)
                seen_questions.append(next_question)

            # fill up the explore questions with random questions that haven't been seen already and weren't just picked
            while len(explore_questions) < explore_size:
                explore_questions.append(self.get_random(user_state, exclude_pks=[q.pk for q in seen_questions]))

            # Create the qandas
            for question in exploit_questions:
                QandA.objects.create(question=question, block=new_block, qanda_type='exploit')

            for question in explore_questions:
                QandA.objects.create(question=question, block=new_block, qanda_type='explore')

            user_state.current_session.current_block = new_block
            user_state.current_session.save()



