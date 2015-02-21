
### FORMS.PY
###
### This file defines all of the forms that the experiment will rely on.
### Django streamlines the construction and processing of forms, and we're
### going to take advantage of it. The syntax for creating a form in Django
### is highly similar to the syntax for creating models: We create a class
### for each form, then, for each entry of the form, we provide a name and
### type. See below for examples, and the internet for more information.

# Necessary import to grab Django's form library.
from django import forms
from django.forms.widgets import *

# The login form! This has only two fields: the username and the password
# of the user. Both are simply character fields, restricted to 30 characters,
# as Django doesn't support usernames or passwords longer than that anyway.
class LoginForm(forms.Form):
    username = forms.CharField(max_length = 30)
    password = forms.CharField(max_length = 30,
                               widget = PasswordInput())



# The dogform is the form that the user's are given when they are doing a
# trial. The 7 inputs are the days of the week, and are meant to be filled
# in with how much food the user would like to feed the dog on that day of
# the trial.
class DogForm(forms.Form):
    Monday    = forms.DecimalField(max_digits = 5, decimal_places = 2, required = False, widget = forms.TextInput(attrs={'class': 'response'}))
    Tuesday   = forms.DecimalField(max_digits = 5, decimal_places = 2, required = False, widget = forms.TextInput(attrs={'class': 'response'}))
    Wednesday = forms.DecimalField(max_digits = 5, decimal_places = 2, required = False, widget = forms.TextInput(attrs={'class': 'response'}))
    Thursday  = forms.DecimalField(max_digits = 5, decimal_places = 2, required = False, widget = forms.TextInput(attrs={'class': 'response'}))
    Friday    = forms.DecimalField(max_digits = 5, decimal_places = 2, required = False, widget = forms.TextInput(attrs={'class': 'response'}))
    Saturday  = forms.DecimalField(max_digits = 5, decimal_places = 2, required = False, widget = forms.TextInput(attrs={'class': 'response'}))
    Sunday    = forms.DecimalField(max_digits = 5, decimal_places = 2, required = False, widget = forms.TextInput(attrs={'class': 'response'}))



# The diagnostic form! This has several fields, one per question we
# wish to ask the user.
class DiagnosticForm(forms.Form):
    question_1 = forms.DecimalField(max_digits = 5, decimal_places = 2, widget = forms.TextInput(attrs={'class': 'diagnostic'}))
    question_2 = forms.DecimalField(max_digits = 5, decimal_places = 2, widget = forms.TextInput(attrs={'class': 'diagnostic'}))
    question_3 = forms.DecimalField(max_digits = 5, decimal_places = 2, widget = forms.TextInput(attrs={'class': 'diagnostic'}))
    question_4 = forms.DecimalField(max_digits = 5, decimal_places = 2, widget = forms.TextInput(attrs={'class': 'diagnostic'}))
    
