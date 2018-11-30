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
    def get_random(user_state):
        # This will return a random question /qanda that hasn't been asked yet in this session
        if user_state.current_session:
            seen_pks = [qanda.question.pk for qanda in user_state.session_history]
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

        if user_state.current_session.is_complete:
            return

        if user_state.current_session.current_block.is_complete:

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

        if user_state.current_session.is_complete:
            return

        if user_state.current_session.current_block.is_complete:

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

        if user_state.current_session.is_complete:
            return

        # Check if the current block now complete after you added the answer
        if user_state.current_session.current_block.is_complete:

            # Get the previous exploit questions
            exploit_previous = user_state.current_session.current_block.all_qandas.filter(qanda_type='exploit')
            exploit_previous_correct = exploit_previous.filter(answer_correct=True)

            # If they got them all right, increase split by 0.1, if only one wrong increase by 0.05
            difference = abs(len(exploit_previous) - len(exploit_previous_correct))
            split_val = 0.05
            values = {0: 0.15, 1: 0.1}
            if difference in values:
                split_val = values[difference]
            split = user_state.current_session.increment_split(split_val)

            # The ratio between explore and exploit in the block
            explore_size = ceil(user_state.current_session.block_size * split)
            exploit_size = user_state.current_session.block_size - explore_size

            # Get the list of the pks to explore. This is just the list that represents the model
            model = self._get_model(user_state)

            # Get the all the wrongly answered questions
            wrong_qandas = user_state.session_history.filter(answer_correct=False)
            seen_qandas = user_state.session_history.all()
            seen_questions = [qanda.question for qanda in seen_qandas]

            # make the block
            new_block = Block.objects.create(session=user_state.current_session)

            '''
            To get the explore questions, you iterate over the model, looking for the first (most difficult)
            questions that haven't been seen yet. 
            '''
            explore_qandas = []
            for pk in model:
                question = Question.objects.get(pk=pk)
                if question not in seen_questions:
                    explore_qandas.append(QandA.objects.create(question=question,
                                                               block=new_block,
                                                               qanda_type='explore'))
                if len(explore_qandas) >= explore_size:
                    break

            '''
            To get the exploit questions. There might be a lot of wrong questions, you need to pick which ones are 
            most worthwhile for the learner to see. Look at all the questions that they have got wrong so far 
            and find out which ones are most difficult according to the model. 
            For each of these, you can then find the similar questions that haven't been seen yet 
            and put them into the block.
            '''

            # Create a list of the wrong questions and their postions within the model
            # tuples = [(wrong_q.question.pk, model.index(wrong_q.question.pk)) for wrong_q in wrong_qandas]

            tuples = []
            for wrong_q in wrong_qandas:
                a = wrong_q.question.pk
                b = model.index(wrong_q.question.pk)
                tuples.append((a, b))

            # sort these on the position to get the highest pks
            tuples = sorted(tuples, key=lambda y: y[1])

            exploit_qandas = []
            for tup in tuples[:exploit_size]:
                pk = tup[0]
                similar = matrix.get_similar_question_pks(pk)
                for similar_pk in similar:
                    question = Question.objects.get(pk=similar_pk)
                    if question not in seen_questions:
                        exploit_qandas.append(QandA.objects.create(question=question,
                                                                   block=new_block,
                                                                   qanda_type='exploit'))
                        break

            user_state.current_session.current_block = new_block
            user_state.current_session.save()

    @staticmethod
    def _get_model(user_state):

        '''
        This function creates a basic model to allow for some prediction. It starts by getting the
        history of all of the right and wrong answers from the sitting (current test, collection of sessions)
        and gets the comparisons from the matrix based on the pk of the question. If the questions was answered correctly
        the order of the values is reversed.
        Then a dict is created that keeps track of the comparison scores and and the total of their indices in the lists
        Then the questions are sorted by the score that is assigned to it.

        You might also need to filter out the questions that have already been seen and the questions
        with the same sentences that have already been seen?

        you might want to use numpy here to make this faster, you are dealing with big arrays.
        :param user_state:
        :return: a list of all the question pk, sorted from hardest to easiest
        '''

        # For each qanda object in this sitting, get the comparison values for the questions with right answers
        value_lists = []
        for qanda in user_state.session_history:
            values = matrix.get_similar_question_pks(qanda.question.pk)
            # If they got the answer correct, reverse the list
            if qanda.answer_correct:
                values = reversed(values)

            value_lists.append(values)

        # create the scores
        scores = {}
        for i, values in enumerate(zip(*value_lists)):

            for comparison_value in values:
                scores[comparison_value] = i if comparison_value not in scores else scores[comparison_value] + i

        tuples = [(key, val) for key, val in scores.items()]
        tuples = sorted(tuples, key=lambda x: x[1])
        return [pk for pk, val in tuples]



