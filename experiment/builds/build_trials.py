
# A couple of essential imports. We'll need random.uniform to be able to
# randomly assign income values when desired, shuffle so that we can randmoize
# the order of the life cycles, and xlrd is so that we can read the Excel
# document where the trials are stored.
from   random  import uniform, shuffle
from   ..helpers import k
import xlrd

""" TRIAL
    The trial class is going to represent a single round of the game. Trials
    will vary in certain aspects, including the number of days in the trial,
    the interest rates, and the amount of cash given to the user on each day.
    They will also be dichotomized into static and dynamic, but this is
    primarily a difference in user experience, not in coding, so it will not
    matter here.

    PARAMETERS
    incomes   -- A vector of integers, each representing how many bucks the
                 user will be given each day. The length of the vector will
                 match the number of periods for this trial. It will have the
                 a length 1 greater than the length of the interests vector,
                 described next.
    interests -- Another vector of integers, this time representing the
                 interest rates for each day. The vector will have a length
                 1 less than the length of the incomes vector, due to the fact
                 that income is allotted in all periods, but interest does not
                 accumulate on the last day (because there is no next day).
"""
class trial:

    def __init__(self, incomes, interests):
        self.incomes   = incomes
        self.interests = interests
        
        # Whenever we print a trial, we print the days of the week too.
        # We only want to print as many as needed though.
        days      = ["Monday", "Tuesday",  "Wednesday", "Thursday",
                     "Friday", "Saturday", "Sunday"]
        self.days = days[0:len(incomes)]

    def __repr__(self):
        text = "Trial Object: (length %i)" % len(self.incomes)
        return text


    """ Returns a comma-separated list of the incomes. """
    def get_incomes(self):
        values = ""
        for income in self.incomes:
            values += "%i," % income
        return values[:-1]


    """ Returns a comma-separated list of the incomes. """
    def get_interests(self):
        values = ""
        for interest in self.interests:
            values += "%i," % interest
        return values[:-1]


    """ We'll need to know the optimal solution to the decision problem.
        This method finds it for us. """
    def calculate_optimum(self):

        # The optimal solution relies on the food-to-wag function. This
        # function is of the form wags = food^k, where k is a constant.
        # Grab k, defined in helpers
        from ..helpers import k

        # The list we'll be building
        optimum = []

        # Extend the interest vector for simplicity, and convert it
        interests = self.interests
        interests.append(0)
        interests = map(lambda x: float(x) / 100 + 1, interests)

        
        # First of all, calculate the optimal spending for the first day.
        # This will be instrumental in calculating the optimal spending
        # for all subsequent days.
        numerator = 0
        for day in range(len(self.days)):
            interest = 1
            for later_day in range(day,len(self.days)):
                interest *= interests[later_day]
            numerator += float(self.incomes[day]) * interest
        print numerator

        denominator = 0
        for day in range(len(self.days)):
            interest = 1
            for later_day in range(day, len(self.days)):
                interest *= interests[later_day]
            denominator += pow(interest, 1. / (1 - k))
        optimum.append(round(numerator / denominator, 2))


        # Now calculate the optimum value for every subsequent day
        for day in range(1, len(self.days)):
            interest = 1
            for earlier_day in range(day):
                interest *= interests[earlier_day]
            optimum.append(round(pow(interest, 1 / (1 - k)) * optimum[0], 2))

        # Done. Return the optimum.
        return optimum


""" Every user has a list of trials to complete during the experiment. The
    ordering of these trials is individualized, but organized. To begin with
    there are 2 training trials. These are the same across all users, and always
    come first.

    Next are the actual experimental trials. The experimental trials are split
    into 3 "life cycles", each with a different structure. The differences in
    structure are important for analytical reasons, but not for constructing
    the trials, so I won't go into details. What is important is the difference
    between the two user classes:

    STATIC:  The static users receive 5 trials per life cycle.
    DYNAMIC: The dynamic users receive only 1 trial per life cycle.

    These are the only real differences in constructing the trials for the two
    classes. Static users have many more trials to answer, and so there are
    more trials to build. All of the trials are pre-made, and can be found in
    the Excel document 'trials.xls'.
"""
def build_trials(user_class):

    # Grab the trial data.
    file_name = "experiment/builds/trials.xls"
    data      = xlrd.open_workbook(file_name)

    # Construct the dictionary that will hold all of the trials. This
    # has only two entries: the training trials and the experimental trials.
    trials = []


    # First thing's first: Build the training trials. Grab the number of
    # training questions and build them all.
    training_data       = data.sheet_by_name("training")
    base                = {"row": 2, "col": 1}
    num_training_trials = int(training_data.cell(base["row"] + 1,
                                                 base["col"] - 1).value)
    for index in range(num_training_trials):
        row_incomes   = base["row"] + 2*index
        row_interests = base["row"] + 2*index + 1

        # Scroll through the row and grab the income and interest values
        income_values   = cleanse(training_data.row_values(row_incomes)[base["col"]:])
        interest_values = cleanse(training_data.row_values(row_interests)[base["col"]:])
        trials.append(trial(income_values, interest_values))


    # Now, depending on whether the user is static or dynamic, we have two
    # branches to take. If the user is static, we pull the trials from the
    # 'static' sheet of the Excel file; otherwise we pull from the 'dynamic'
    # sheet. In either case we want to randomize the order of the life cycles.
    data        = data.sheet_by_name(user_class)
    cycle_order = range(1,4)
    shuffle(cycle_order)
    for life_cycle in cycle_order:
        trials.extend(build_life_cycle(data, life_cycle))

    # Done. Return the trials
    return trials



""" Every life cycle is formatted the exact same way within the Excel document.
    This method takes advantage of that uniformity to simplify translating
    the trial data. The start of every life cycle is indicated by a label in
    the first column of the data sheet: "LIFE CYCLE XXX" where XXX is the number
    of the life cycle. The cell directly below this contains the number of
    trials in the life cycle. Together, that's all the information we'll need
    to build the cycle.
"""
def build_life_cycle(data, cycle):

    # First task: Find the base address of the current life cycle.
    label    = "LIFE CYCLE %i" % cycle
    base     = {"row": 2, "col": 1}
    while True:
        if data.cell(base["row"], 0).value == label:
            break
        else:
            base["row"] += 1

    # Found the base address. Grab the number of trials.
    num_trials = int(data.cell(base["row"] + 1, 0).value)

    # Time to build the trials.
    trials = []
    for index in range(num_trials):
        row_incomes   = base["row"] + 2*index
        row_interests = base["row"] + 2*index + 1

        # Scroll through the row and grab the income and interest values
        income_values   = cleanse(data.row_values(row_incomes)[base["col"]:])
        interest_values = cleanse(data.row_values(row_interests)[base["col"]:])
        trials.append(trial(income_values, interest_values))

    # Got em all. Shuffle them to randomize the order, and then return the
    # life cycle.
    shuffle(trials)
    return  trials



""" Every trial must be converted from its Excel format to a Python-friendly
    format. xlrd takes care of most of the work by exchanging the values
    from Excel to Python; the rest of the work is just extra formatting.

    A couple of things need to be done. Firstly, we need to convert all of the
    numerica values to integers. They ought to already be integers, but xlrd
    interprets them as floats by default.

    Secondly, some of the values in Excel will be strings, either '-' or 'RAND'.
    In the former case, we interpret this to mean there is no value for the
    given day, and the trial is over. In the latter case, we are looking to
    generate a random number.
"""
def cleanse(values):
    for index in range(len(values)):
        value = values[index]

        # Try to convert to an integer.
        try:
            values[index] = int(value)

        # If that failed, it's because the value isn't an integer. In
        # this case, it's either the string '-' or 'RAND'. In the former
        # instance, this indicates that the given day is not used in the
        # current trial. In the latter instance, it's because a random
        # value is to be generated.
        except:
            if value == "-":
                values = values[:index]
                break
            else:
                values[index] = int(uniform(20,200))
    return values
