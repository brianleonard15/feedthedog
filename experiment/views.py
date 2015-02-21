
# Django imports
from django.shortcuts               import render_to_response
from django.contrib.auth            import authenticate, login, logout
from django.http                    import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

# Python imports
import math

# Local imports
from forms   import LoginForm, DogForm, DiagnosticForm
from models  import TrialAnswer, DiagnosticAnswer
from helpers import calculate_days, process_input, calculate_wags


##################
### LOGIN_USER ###
##################

""" Logs in a user. The user is prompted to give a username and
    password. We attempt to match their input to a user in Django's
    User model; if there is one, and if it is active, we login the
    user. Otherwise, we handle the case appropriately. """
def login_user(request):
    anonymous = request.user.is_anonymous

    # If the form has been submitted, let's check the inputs.
    if request.method == "POST":
        form = LoginForm(request.POST)

        # If the form is valid -- i.e. the inputs are non-empty -- then
        # redirect the page to the login screen.
        if form.is_valid():
            username_input = form.cleaned_data["username"]
            password_input = form.cleaned_data["password"]

            # Now to determine if the username and password are valid.
            user = authenticate(username = username_input,
                                password = password_input)
            
            if user is not None:                # The user exists!
                if user.is_active:              # A successful login!
                    login(request, user)
                    return HttpResponseRedirect("/consent/")

                else:                           # User exists but isn't active.
                    context = {"user": request.user, "form": form,  "anonymous": anonymous, "already_done": True}
                    
            else:                               # The user does not exist.
                context = {"user": request.user, "form": form, "anonymous": anonymous, "bad_login": True}
                
        # We've got an issue with the input: One of the fields is blank.
        else:
            context = {"user": request.user, "form": form, "anonymous": anonymous}
            
    # Form has not been submitted yet. Give the user the default login.html
    # page.
    else:
        form = LoginForm()
        context = {"user": request.user, "form": form, "anonymous": anonymous, "bad_login": False}

    # For any result but a successful login, render 'login.html' with the
    # given parameters.
    return render_to_response("login.html", context)



###################
### LOGOUT_USER ###
###################

""" Logs out a user. After logging them out, redirect them to the
    login screen. """
def logout_user(request):
    logout(request)
    return render_to_response("logout.html", {})



###############
### CONSENT ###
###############

""" Displays the consent form. """
@login_required
def consent(request):
    context = {'user': request.user}
    return render_to_response("consent.html", context)



####################
### INSTRUCTIONS ###
####################

""" Displays the experiment's instructions. """
@login_required
def instructions(request):
    
    context = {"user": request.user}
    return render_to_response("instructions.html", context)



################
### EXAMPLES ###
################

""" Displays a couple of examples. """
@login_required
def examples(request):

    # The examples that we give are going to differ if the user is on
    # the static arm or the dynamic arm.
    user_class = request.user.get_profile().user_class
    context    = {"user": request.user, "dynamic": user_class == "dynamic"}
    return render_to_response("examples.html", context)


################
### TRAINING ###
################

""" Before the user gets to enjoy the experiment itself, we present them
    with a few training examples. This method grabs the user's training
    examples and passes them along to the page. """
@login_required
def training(request):

    # If the user has finished the training session, redirect them.
    if request.user.get_profile().finished_training:
        return HttpResponseRedirect("/experiment/")

    # If the trial form has been submitted, let's check the inputs.
    if request.method == "POST":
        form = DogForm(request.POST)

        if form.is_valid():
            trials_done_before = request.user.get_profile().trials_done
            process_input(form, request.user, True)
            trials_done_after  = request.user.get_profile().trials_done

            # If they completed a trial in this submission -- not necessarily
            # a given for dynamic users -- we send them to check out their
            # feedback.
            if trials_done_after != trials_done_before:
                return HttpResponseRedirect("/training/review/")
                
    # Load the form.
    form = DogForm(auto_id = "whatever")

    # Grab the problem.
    profile       = request.user.get_profile()
    problem_index = profile.trials_done
    trial_object  = TrialAnswer.objects.filter(user     = request.user,
                                               question = problem_index)[0]
    

    # Reconstruct the trial
    from builds.build_trials import trial
    problem      = trial(trial_object.incomes.split(","), trial_object.interests.split(","))
    days_to_show = problem.days[:-1] if    profile.user_class == "static" \
                                     else [profile.day]
    days_inputs  = calculate_days(problem, request.user)
    user_class   = profile.user_class

    # Create the info for the dynamic users.
    today_index     = problem.days.index(profile.day)

    # If they're dynamic, we'll want to show how much they've spent
    # per day.
    spendings = trial_object.responses
    if spendings:
        spendings = map(float, spendings.split(','))
        spendings.extend(["-"]*(len(problem.days) - len(spendings)))
    else:
        spendings = ["-"]*len(problem.days)

    # We want to inform them how much money they can spend today. To do
    # so, we'll tell them how much money they actually have, plus how much
    # they can borrow from future days. First, calculate how much money they
    # have currently.
    incomes   = map(float, problem.incomes)
    interests = map(float, problem.interests)
    carry_over = 0
    for index in range(today_index):
        carry_over += incomes[index] - spendings[index]
        carry_over *= (interests[index] / 100. + 1)
    today_money = round(carry_over + incomes[today_index], 2)
    

    # Now calculate how much they can borrow.
    borrowable = float(incomes[-1])
    for day in reversed(range(today_index, len(interests))):
        borrowable = borrowable / (1 + interests[day] / 100.) + (incomes[day] if day != today_index else 0)
    borrowable = round(borrowable, 2) 

    # The amount of cash we can spend today is how much we have physically
    # plus how much we can borrow
    spendable = today_money + borrowable

    # Fill up the dictionary with all the info we'll need.
    dynamic_info = {"money":     today_money, "borrowable": borrowable,
                    "spendable": spendable,   "spendings":  spendings}

    context      = {"user":      request.user, "problem":     problem,
                    "days":      days_to_show, "days_inputs": days_inputs,
                    "form":      form,         "index":       problem_index + 1,
                    "dynamic":   dynamic_info, "class":       profile.user_class}
    return render_to_response("training.html", context)



#######################
### TRAINING REVIEW ###
#######################

""" After the training examples we want to display some feedback for the user.
    All this includes is the amount they paid per day of the given trial,
    how much the dog ate, and how much the optimum answer would have allotted
    per day. """
@login_required
def training_review(request):

    # Grab the user's profile
    profile = request.user.get_profile()

    # We want to grab the most recent answer.
    from builds.build_trials import trial
    current_problem_index = profile.trials_done - 1
    trial_object          = TrialAnswer.objects.filter(user     = request.user,
                                                       question = current_problem_index)[0]

    trial                 = trial(trial_object.incomes.split(','),
                                  trial_object.interests.split(','))
    days_to_show          = trial.days
    responses             = trial_object.responses.split(',')
    wags                  = [calculate_wags(float(food)) for food in responses]
    optimum               = trial.calculate_optimum()
    optimum_wags          = map(calculate_wags, optimum)
    totals                = {"wags":    reduce(lambda x, y: x + y, wags,         0),
                             "optimum": reduce(lambda x, y: x + y, optimum_wags, 0)}

    # Update the user's finished_training variable if necessary.
    if profile.trials_done == 2:
        next_url = "experiment"
        done     = True
    else:
        next_url = "training"
        done     = False


    # Collect all of the info to show.
    days = [{"day":          days_to_show[index], "response": responses[index],
             "wags":         wags[index],         "optimum":  optimum[index],
             "optimum_wags": optimum_wags[index]} for index in range(len(days_to_show))]
    context = {"user": request.user, "days": days, "totals": totals,
               "url":  next_url,     "done": done}
    return render_to_response("training_review.html", context)


##################
### EXPERIMENT ###
##################

@login_required
def experiment(request):

    # Get the profile
    profile = request.user.get_profile()

    # If the user has finished the training session, redirect them.
    if profile.finished_experiment:
        return HttpResponseRedirect("/diagnostics/")
    elif not profile.finished_training:
        return HttpResponseRedirect("/training/")

    # If the trial form has been submitted, let's check the inputs.
    if request.method == "POST":
        form = DogForm(request.POST)

        if form.is_valid():
            process_input(form, request.user, True)

            # Check to see if they're now done with the experiment
            if request.user.get_profile().finished_experiment:
                return HttpResponseRedirect("/diagnostics/")
                

    # Load the form.
    form = DogForm(auto_id = "whatever")

    # Grab the problem.
    profile       = request.user.get_profile()
    problem_index = profile.trials_done
    trial_object  = TrialAnswer.objects.filter(user     = request.user,
                                               question = problem_index)[0]

    # Reconstruct the trial
    from builds.build_trials import trial
    problem      = trial(trial_object.incomes.split(","), trial_object.interests.split(","))
    days_to_show = problem.days[:-1] if    profile.user_class == "static" \
                                     else [profile.day]
    days_inputs  = calculate_days(problem, request.user)
    user_class   = profile.user_class

        # Create the info for the dynamic users.
    today_index     = problem.days.index(profile.day)

    # If they're dynamic, we'll want to show how much they've spent
    # per day.
    spendings = trial_object.responses
    if spendings:
        spendings = map(float, spendings.split(','))
        spendings.extend(["-"]*(len(problem.days) - len(spendings)))
    else:
        spendings = ["-"]*len(problem.days)

    # We want to inform them how much money they can spend today. To do
    # so, we'll tell them how much money they actually have, plus how much
    # they can borrow from future days. First, calculate how much money they
    # have currently.
    incomes   = map(float, problem.incomes)
    interests = map(float, problem.interests)
    carry_over = 0
    for index in range(today_index):
        carry_over += incomes[index] - spendings[index]
        carry_over *= (interests[index] / 100. + 1)
    today_money = round(carry_over + incomes[today_index], 2)
    

    # Now calculate how much they can borrow.
    borrowable = float(incomes[-1])
    for day in reversed(range(today_index, len(interests))):
        borrowable = borrowable / (1 + interests[day] / 100.) + (incomes[day] if day != today_index else 0)
    borrowable = round(borrowable, 2) 

    # The amount of cash we can spend today is how much we have physically
    # plus how much we can borrow
    spendable = today_money + borrowable

    # Fill up the dictionary with all the info we'll need.
    dynamic_info = {"money":     today_money, "borrowable": borrowable,
                    "spendable": spendable,   "spendings":  spendings}

    context      = {"user":  request.user, "problem":     problem,
                    "days":  days_to_show, "days_inputs": days_inputs,
                    "form":  form,         "dynamic":     dynamic_info,
                    "class": profile.user_class}
    return render_to_response("experiment.html", context)


###################
### DIAGNOSTICS ###
###################

@login_required
def diagnostics(request):

    # Get the profile
    profile = request.user.get_profile()
    
    # If the user is static, they don't take the diagnostic questions.
    # Also, if they're already done with the diagnostics, redirect them.
    if profile.user_class == "static" or profile.finished_diagnostics:
        return HttpResponseRedirect("/payment/")

    # If the user isn't done with the experiment, send them there.
    if not profile.finished_experiment:
        return HttpResponseRedirect("/experiment/")


    # Check if the form has been submitted.
    if request.method == "POST":
        form = DiagnosticForm(request.POST)

        # If the form is valid -- it almost certainly will be; the only way
        # it can possibly fail this test is if the user reports that they
        # did use tools but did not report which -- then go ahead and submit
        # their answer.
        if form.is_valid():
            
            # Grab all of the form fields.
            question_1 = form.cleaned_data["question_1"]
            question_2 = form.cleaned_data["question_2"]
            question_3 = form.cleaned_data["question_3"]
            question_4 = form.cleaned_data["question_4"]

            # Submit the survey!
            DiagnosticAnswer.objects.create(
                user = request.user,
                question_1 = question_1, question_2 = question_2,
                question_3 = question_3, question_4 = question_4)

            # Update their profile to register that they finished
            # the survey.
            profile.finished_diagnostics = True
            profile.save()

            # Finally, redirect the user to the payment page.
            return HttpResponseRedirect("/payment/")

    # Set up the form
    form    = DiagnosticForm(auto_id = "whatever")
    ids     = "'question_1', 'question_2', 'question_3', 'question_4'"
    context = {"user": request.user, "form": form, "ids": ids}
    return render_to_response("diagnostics.html", context)


###############
### PAYMENT ###
###############

@login_required
def payment(request):

    # Grab the profile
    profile = request.user.get_profile()

    # Grab the user's payment trial
    payment_trial = profile.payment_trial
    trial_object  = TrialAnswer.objects.filter(user     = request.user,
                                               question = payment_trial)[0]

    # Reconstruct the trial
    from builds.build_trials import trial
    problem = trial(trial_object.incomes.split(","),
                    trial_object.interests.split(","))

    # Get the responses, the wags, and, the optimal food profile, and the
    # totals.
    days_to_show = problem.days
    responses    = trial_object.responses.split(',')
    wags         = [calculate_wags(float(food)) for food in responses]
    optimum      = problem.calculate_optimum()
    optimum_wags = map(calculate_wags, optimum)
    totals       = {"wags":    reduce(lambda x, y: x + y, wags,         0),
                    "optimum": reduce(lambda x, y: x + y, optimum_wags, 0)}

    # The difference between the optimum solution and the subject's solution
    # is involved in the payment calculation. So is the value b, which
    # is a scaling parameter
    b       = 0.01
    dif     = totals["optimum"] - totals["wags"]
    payment = round(40 - b * (dif**2), 2)

    # Set the payment
    profile.payment = payment
    profile.save()

    # Add on the proper suffix.
    suffix = {2:  "nd", 3:  "rd", 4:  "th", 5:  "th", 6:  "th", 7:  "th", 8:  "th", 9:  "th",
              10: "th", 11: "th", 12: "th", 13: "th", 14: "th", 15: "th", 16: "th", 17: "th"}
    payment_trial += 1
    payment_trial  = str(payment_trial) + suffix[payment_trial]

    # Collect all of the info to show.
    days = [{"day":  days_to_show[index], "response": responses[index],
             "wags": wags[index],         "optimum":  optimum[index]} for index in range(len(days_to_show))]
    context = {"user":    request.user, "days":  days, "totals": totals,
               "payment": payment,      "trial": payment_trial}
    return render_to_response("payment.html", context)
    

    

