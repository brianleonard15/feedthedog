
from math   import sqrt
from models import TrialAnswer

""" This helper method calculates which days we want to display inputs
    for. If the user is static, we show all of the days relevant to the trial
    (minus the last one, for which the user does not input anything). If
    they are dynamic, we need to know which day they are on.
"""
def calculate_days(problem, user):
    days = {"Monday":   True,  "Tuesday": False, "Wednesday": False,
            "Thursday": False, "Friday":  False, "Saturday":  False,
            "Sunday":   False}
    user_class     = user.get_profile().user_class
    if user_class == "static":
        for day in problem.days[0:-1]:
            days[day] = True
    else:
        for day, show in days.iteritems():
            days[day] = False
        days[user.get_profile().day] = True
    return days


""" This helper processes the user's input. The data has already been
    validated, so all we need to do is store it and augment whatever
    variables need updating.
"""
def process_input(form, user, training):
    profile   = user.get_profile()

    # Grab all of the non-meaningless fields.
    responses = filter(lambda x: x != "None",
                       map(str, [form.cleaned_data["Monday"],   form.cleaned_data["Tuesday"], form.cleaned_data["Wednesday"],
                                 form.cleaned_data["Thursday"], form.cleaned_data["Friday"],  form.cleaned_data["Saturday"],
                                 form.cleaned_data["Sunday"]]))

    # Before we can submit the responses, we need to confirm that they're
    # legal responses given the trial's incomes and interests. To do that,
    # send the incomes, interests and responses over to our other helper.
    problem_index = profile.trials_done
    trial_object  = TrialAnswer.objects.filter(user     = user,
                                               question = problem_index)[0]
    from builds.build_trials import trial
    problem = trial(trial_object.incomes.split(","), trial_object.interests.split(","))

    # Add the responses to the trial object.
    trial_object.add_response(user, responses)

    # Check if we're done with the trial. If the user is static, this is
    # automatically true. If they're dynamic, we need to check that the
    # current day is the last day of their trial. First we need to get the
    # trial itself to confirm this.
    problem_index = profile.trials_done
    trial_object  = TrialAnswer.objects.filter(user     = user,
                                               question = problem_index)[0]

    done_with_trial =  profile.user_class == "static"  or \
                      (profile.user_class == "dynamic" and profile.day == problem.days[-2])

    # If we're done with the trial, update the trials_done counter
    # and check if we're now done with the training session or the
    # experiment itself.
    if done_with_trial:
        profile.trials_done = profile.trials_done + 1
        profile.day         = "Monday"

        # Validate the responses
        trial_object.validate()

        # If there are 2 trials completed, we just finished the training.
        if profile.trials_done == 2:
            profile.finished_training = True

        elif (profile.user_class == "static"  and profile.trials_done == 17) or \
             (profile.user_class == "dynamic" and profile.trials_done == 5):
            profile.finished_experiment = True

    # If we're NOT done with the current trial, then we can infer that
    # we are a dynamic user, and we need to update the day variable.
    else:
        # If the user is dynamic, update their day variable automatically.
        next_day = {"Monday":   "Tuesday", "Tuesday": "Wednesday", "Wednesday": "Thursday",
                    "Thursday": "Friday",  "Friday":  "Saturday",  "Saturday":  "Sunday",
                    "Sunday":   "Monday"}
        profile.day = next_day[profile.day]

    # Save the profile, and we're done!
    profile.save()
    trial_object.save()
    return


""" We may want to change the food-to-wag function. The function will always
    be of the form w = x^k where w is the number of wags, x is the food and
    k is some constant. k may change, however, so we are best off leaving it
    as a variable.
"""
k = 0.5
def calculate_wags(food):
    global k
    wags = round(pow(food, k), 2)
    return wags
