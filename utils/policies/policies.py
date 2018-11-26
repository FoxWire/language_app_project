from lang_app.models import Question, QandA, Session, Block
from utils.matrix_wrapper import MatrixWrapper
from random import choice, randint

# matrix = MatrixWrapper()


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


        return Question.objects.all()[randint(1, 1000)]

        # if not user_state.current_session:
        #
        #     # Create the new session
        #     new_session = user_state.create_session()
        #     # Create the new block for the session
        #     new_block = Block.objects.create(session=new_session, block_type='explore')
        #
        #     # Fill up the new block with random qandas
        #     while not new_block.is_full:
        #         QandA.objects.create(question=self.get_random(user_state), block=new_block)
        #
        #     # Add the new block
        #     user_state.add_block(new_block)
        #
        # return user_state.current_session.current_block.get_question()

    def update_state(self, user_state, question_pk, answer, correct_bool): pass

    @staticmethod
    def get_random(user_state):
        # This will return a random question /qanda that hasn't been asked yet in this session
        if user_state.current_session:
            seen_pks = [qanda.question.pk for qanda in user_state.session_history]
            qs = Question.objects.exclude(pk__in=seen_pks)
        else:
            qs = Question.objects.all()
        return choice(list(qs))

    def switch_policy(self):
        pass


class PolicyOne(Policy):

    """
    This policy will just create a block of random questions each time.
    """

    def update_state(self, user_state, question_pk, answer, correct_bool):

        # Update with the answer from the user
        user_state.current_session.current_block.add_answer(question_pk, answer, correct_bool)

        if user_state.current_session.current_block.is_complete:

            # Create a new block ...
            new_block = Block.objects.create(session=user_state.current_session, block_type='explore')

            # Fill up the new block with random qandas
            while not new_block.is_full:
                QandA.objects.create(question=self.get_random(user_state), block=new_block)

                user_state.current_session.current_block = new_block
                user_state.current_session.save()


class PolicyTwo(Policy):
    """
    After the initial block of random questions, this policy will fill the next block with
    similar questions to ones that were previously failed (answered wrongly). It will attempt
    to fill the block with as many of these as possible and add random questions if there are
    not enough.
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

        if user_state.current_session.current_block.is_complete:

            # Create a new block
            new_block = Block.objects.create(session=user_state.current_session, block_type='explore')

            for failed_qanda in user_state.current_session.failed_qandas:

                # For each of the failed qandas, find the next most similar question that doesn't have the same
                # sentence and hasn't been see already. The default is a random question
                next_question = self.get_random(user_state)
                for pk in matrix.get_similar_pks(failed_qanda.pk):
                    question = Question.objects.get(pk=pk)
                    seen_questions = [qanda.question for qanda in user_state.session_history]

                    if question.sentence is not failed_qanda.question.sentence and question not in seen_questions:
                        next_question = Question.objects.get(pk=pk)
                        break

                # Create the qanda object for the pk that you just found
                QandA.objects.create(question=next_question, block=new_block)

            # If the block is not yet filled up, add some more random questions
            while not new_block.is_full:
                QandA.objects.create(question=self.get_random(user_state), block=new_block)


class PolicyThree(Policy):
    
    """
    After the initial set of random questions, this policy will attempt to find the most difficult
    questions based on all of the answers given so far.
    Each block will consist of an explore and exploit phase and the focus will shift from
    more explore to more exploit over the course of the session.
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

        # Check if the current block now complete after you added the answer
        if user_state.current_session.current_block.is_complete:

            # If this is an explore block, move on to the exploit block
            if user_state.current_session.current_block.next_block:
                user_state.current_session.current_block = user_state.current_session.current_block.next_block
                user_state.save()
            else:
                # Otherwise, the current (finished block) must be an exploit block, so create two more blocks
                explore_pks = self._get_explore_questions(user_state)
                exploit_questions = user_state.current_session.get_history().filter(answer_correct=False)

                # Create the explore block and put the questions in it
                explore_block = Block.objects.create(session=user_state.current_session, block_type='explore')
                for pk in explore_pks[:10]:
                    question = Question.objects.get(pk=pk)
                    QandA.objects.create(question=question, block=explore_block)

                user_state.current_session.current_block = explore_block
                user_state.save()

                # Create the exploit block and put the questions in it
                exploit_block = Block.objects.create(session=user_state.current_session, block_type='exploit')
                for qanda in exploit_questions[:10]:
                    qanda.block = exploit_block

                explore_block.next_block = exploit_block
                explore_block.save()

    @staticmethod
    def _get_explore_questions(user_state):

        '''
        This function creates a basic model to allow for some prediction. It starts by getting the
        history of all of the right and wrong answers from the sitting (current test, collection of sessions)
        and gets the comparisons from the matrix based on the pk of the question. If the questions was answered correctly
        the order of the values is reversed.
        Then a dict is created that keeps track of the comparison scores and and the total of their indices in the lists
        Then the questions are sorted by the score that is assigned to it.

        You might also need to filter out the questions that have already been seen and the questions
        with the same sentences that have already been seen?
        :param user_state:
        :return:
        '''

        # For each qanda object in this sitting, get the comparison values for the questions with right answers
        value_lists = []
        for qanda in user_state.session_history:
            values = matrix.get_values_for_row(qanda.question.pk)
            # If they got the answer correct, reverse the list
            if qanda.answer_correct:
                values = reversed(values)
                value_lists.append(values)

        # create the scores
        scores = {}
        for i, values in enumerate(zip(value_lists)):
            for comparison_value in values:
                scores[comparison_value] = i if comparison_value not in scores else scores[comparison_value] + i

        tuples = [(key, val) for key, val in scores.items()]
        tuples = sorted(tuples, key=lambda x: x[1])
        return [pk for pk, val in tuples]


