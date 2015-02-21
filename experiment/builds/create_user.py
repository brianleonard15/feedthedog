
### CREATE_USER.PY
###
### This file is responsible for creating users, a process involving several
### stages. First of all, when we make a user, we require that user to have
### a username and password. Both of these will be supplied by he who calls
### the method below; note that both the username and password must be 30
### characters or fewer, or Django cannot store them. Once we have a valid
### username and password for the new user, we add them to Django's own
### User model

# Import the Django User model and a method for storing the User object.
# I'm not entirely sure why we need post_save, but it seems to be required
# to use our own user profiles.
from django.contrib.auth.models import User, UserManager
from django.db.models.signals   import post_save

# Import the choice function from Python's random library. This will be
# useful for randomzing the ordering of domains and questions.
from random import shuffle, uniform, choice

# Import our own UserProfile model
from ..models     import UserProfile, TrialAnswer
from build_trials import build_trials


""" Method to create a new user profile. sender is the User model, instance
    is the precise instantiation of the User object that we wish to correlate
    with our new profile, created appears to be boolean (I believe this
    represents whether or not the save() call actually created a new User
    object -- if it didn't, we obviously don't want to create a new profile),
    and **kwargs could be anything. This system is mysterious to me, but I'm
    going to leave it to faith that the internet is not steering me awry. I'm
    guessing that the obscurity of this declaration is due to some backend work
    performed by Django. """
def create_user_profile(sender, instance, created, **kwargs):
    if created:

        # We want to randomly pick a trial for the user's payment.
        max_trial     = 17 if user_class == "static" else 5
        payment_trial = choice(range(2, max_trial))
        
        # Create the actual UserProfile object.
        UserProfile.objects.create(user = instance, payment_trial = payment_trial)

# I think this call is to indicate that the User model should also call
# create_user_profile after a save. 
post_save.connect(create_user_profile, sender=User)


# Here's the method that actually creates the user. First we will create a
# User object, then we create a profile.
def add_user(new_username, new_password, user_class = None):

    # Boolean to represent whether we will actually add a new user or
    # not. This may be set to false if the username already exists and
    # we choose not to overwrite.
    create = True

    # First check to see if that username already exists.
    already_exists = User.objects.filter(username = new_username)
    if already_exists:

        # Ask the user if they want to overwrite
        prompt    = "Username %s already exists. Do you want to overwrite? (yes/no)  " % new_username
        overwrite = raw_input(prompt)

        while overwrite != "yes" and overwrite != "no":
            overwrite = raw_input("Please enter yes or no.  ")

        # If they want to overwrite, then delete the old entry.
        if overwrite == "yes":
            already_exists.delete()

        # Otherwise, set create to False so we don't attempt to make a
        # new identical user.
        else:
            create = False

    # Create the new instance and save it to the database.
    if create:
        new_user = User.objects.create_user(username = new_username,
                                            email    = "fake@fake.com",
                                            password = new_password)

        # Set the user's class. If this hasn't been specified already,
        # or if it is set to something other than 'static' or 'dynamic'
        # then we've got an issue.
        if not user_class:
            user_class = raw_input("What class should the user be? Enter 'static' or 'dynamic': ")

        classes = ["static", "dynamic"]
        while user_class not in classes:
            user_class = raw_input("The user's class must be either 'static' or 'dynamic'. You entered %s. Please choose one of the two: " % user_class)

        # Got an acceptable user class.
        profile            = new_user.get_profile()
        profile.user_class = user_class
        profile.save()
            
        # Time to build the trial objects to be populated by this user.
        user_trials = build_trials(user_class)
        index = 0
        for trial in user_trials:
            TrialAnswer.objects.create(user      = new_user,
                                       question  = index,
                                       incomes   = trial.get_incomes(),
                                       interests = trial.get_interests())
            index += 1
                
        print "New user %s successfully created!" % new_username
        return new_user

    
