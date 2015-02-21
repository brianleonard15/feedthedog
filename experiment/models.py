
# Necessary import to be able to use Django's model library.
from django.db import models

# Another import, this one to allow us to sync our own UserInfo database
# with a given user from Django's User database.
from django.contrib.auth.models import User

""" USER
    The user model holds all of the information pertaining to a given user,
    aside from the username and password; these are held by Django's own
    User model. Instead, this model holds all the extra information associated
    with a user, including the following:
        1) A boolean value representing whether the user has finished the
           experiment.
        2) Their answers to the 26 questions. Admittedly, this implementation
           is pretty clunky. Ideally we would have an easy way of storing 26 (or
           X many) decimals, but Django (and really databases in general) don't
           support lists very well. This is the approach I've taken, if you,
           future developer, see a better way to do it, by all means...
        3) The ordering of the domains. This will just be stored as a string.
        4) The ordering of the questions. This will also be stored as a string.
        5) The number of questions the user has answered thus far.
        6) The payment that the user will receive. This will only be computed
          after the user has finished the experiment.
"""
class UserProfile(models.Model):

    # The User object that this profile corresponds to.
    user = models.OneToOneField(User)


    # Every user is going to be facing either the static or dynamic arm.
    # We control which with the user_class variable. user_class will be
    # set to either "static" or "dynamic" to indicate which class the
    # user belongs to.
    user_class = models.CharField(max_length = 7)


    # Keep track of which trial we're on. If the user is dynamic, we also need
    # to know which day they are on.
    trials_done = models.IntegerField(default = 0)
    day         = models.CharField(max_length = 9, default = "Monday")


    # A bunch of Booleans to represent where the user is located in the
    # experiment.
    finished_training    = models.BooleanField(default = False)
    finished_experiment  = models.BooleanField(default = False)
    finished_diagnostics = models.BooleanField(default = False)


    # Finally, the payment.
    payment       = models.DecimalField(max_digits = 6, decimal_places = 2, default = "0.00")
    payment_trial = models.IntegerField()


    # Return URL. This is only relevant to TESS subjects, as it holds the
    # URL that the user should return to once they have completed the survey.
    return_url = models.CharField(max_length = 150, default = "")



""" TRIAL ANSWER
    This model will store each user's answers to each trial. Every answer
    to every trial from the experimental half of the project from every
    user that participates will be stored here. Each entry into the model has
    four components: the User that the entry belongs to, the number of the
    question that they are answering, their answer to that question, and the
    percent they were off by.

    FIELDS
    user        The User object corresponding to who this answer belongs to. This
                is to identify who created this answer.
    question    The user's question-index. If this question was the user's
                nth question, this field will be set to n.

    And then a crap ton of variables to hold the info about the trial at hand
    and the user's responses to it.
    
"""
class TrialAnswer(models.Model):
    user     = models.ForeignKey(User)
    question = models.IntegerField()

    # Info about the question
    incomes   = models.CommaSeparatedIntegerField(max_length = 30)
    interests = models.CommaSeparatedIntegerField(max_length = 30)
    responses = models.CommaSeparatedIntegerField(max_length = 30)


    """ Whenever the user submits a response we need to add it to the
        trial object. The way in which this is done differs for dynamic
        and static users. If the user is static, we just set self.responses
        equal to response; if the user is dynamic, however, we need to add
        to self.responses rather than reset it.
    """
    def add_response(self, user, response):

        # When we get the responses, they're in a list form.
        response = ','.join(response)
        
        if user.get_profile().user_class == "static":
            self.responses      = response
        else:
            if self.responses:
                self.responses += "," + response
            else:
                self.responses   = response
        self.save()


    """ We need to check that the user's responses are legal. That is, are their
        responses OK for the given trial, given that trial's incomes and interests?
        If they are, then we just return the responses exactly as given, adding. If they're
        not, we change the later responses so that they are legal.
    """
    def validate(self):

        # Couple of initial variables. carry_over represents how much money
        # we have carried from the previous day.
        carry_over = 0.
        index      = 0

        # Convert all the incomes, interests and responses from Django's unicode
        # to floats. It will be helpful to divide everything in interests by 100
        # to change the values from percents to decimal figures.
        incomes   = map(float,                     self.incomes.split(','))
        interests = map(lambda x: float(x) / 100., self.interests.split(','))
        responses = map(float,                     self.responses.split(','))
        
        for response in responses:

            # The first thing we do for every day of the week is find out
            # how much money we could possibly have to spend. This is calculated
            # as the amount of money carried over from the previous day, plus
            # today's income, plus money that we could borrow.
            today_money = carry_over + incomes[index]
            borrowable  = float(incomes[-1])
            for day in reversed(range(index, len(interests))):
                borrowable = borrowable / (1 + interests[day]) + (incomes[day] if day != index else 0)

            # The amount of cash we can spend today is how much we have physically
            # plus how much we can borrow
            spendable = today_money + borrowable

            # If the amount we want to spend is less than what we can spend, then
            # allow it. Otherwise, the amount we get to spend is restricted to
            # to what we can spend.
            if response > spendable:
                responses[index] = round(spendable, 2)
            carry_over = (today_money - responses[index]) * (1 + interests[index])
            index += 1

        # Lastly, give the user whatever's left over to spend on the last day.
        # Convert into CommaSeparatedInteger form
        responses.append(round(carry_over + incomes[-1], 2))
        responses = ','.join(map(str, responses))

        # Save that shit.
        self.responses = responses
        self.save()



""" The responses that a dynamic user has for the diagnostic questions.
"""
class DiagnosticAnswer(models.Model):

    # The user.
    user = models.OneToOneField(User)

    # The questions
    question_1 = models.DecimalField(max_digits = 5, decimal_places = 2)
    question_2 = models.DecimalField(max_digits = 5, decimal_places = 2)
    question_3 = models.DecimalField(max_digits = 5, decimal_places = 2)
    question_4 = models.DecimalField(max_digits = 5, decimal_places = 2)



