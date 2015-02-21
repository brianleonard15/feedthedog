
### BUILD_ALL.PY
###
### A shorthand file for building both the Question and Domain models
### together. If we ever need to delete the database (which will happen
### often enough in development), we can just delete the file from the
### egb directory and run 'python manage.py syncdb' to recreate it given
### the latest definitions of the models. Once we do so, we will probably
### want to reinstantiate the Question and Domain models, and this file
### streamlines that.
import create_user

def build_all():

    # Add in the administrator
    beep = create_user.add_user("admin", "feed_my_dog")
    
