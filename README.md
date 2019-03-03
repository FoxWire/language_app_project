# Language App

## About

Masters project for Software Development Msc at the University of Glasgow.

The aim of the project was to design, implement and test a language learning application that is capable of finding weaknesses in learner syntax and suggest practise sentences. 

The system takes preloaded, example sentences and obtains their structure from NLTK and the Stanford Parser in the form of a parse tree. This tree can then be compared with that of every other sentence in the system via the Zhang-Shasha Tree Edit Distance algorithm. 

The project also explored the idea of using a Gaussian Process as a means of making predictions based on distance between sentences. 

The live site can be found [here](https://sdmiller.pythonanywhere.com)
 
## Installation

1. Clone repo:
    `git clone https://github.com/FoxWire/language_app_project.git`
    (be aware that the sqllite database is under version control - 1.6MB)

2. Create a new virtual environement and install requirements:
    `mkvirtualenv [new_env]`
    `pip install -r requirements.txt`

Because the database is in version control, this is enough to run the local version of the application with `python manage.py runserver`. 
However if you want to set up the full system to parser sentences etc ,there are a few additional steps. This would have to be done when you want to rebuild the 
db for example.

1. Download the stanford parser full from [here](https://nlp.stanford.edu/software/lex-parser.shtml).
    Unzip the file and point your class path to it.


2. The google translate module is needed to construct sentences but it won't work without an api key. If you have a google translate api key,
you can put it file called `api.key` in `language_app_project/utils/google_translate`. Otherwise one can be provided on request.


3. If you did decide to rebuild the database, you'll need to create a new super user account
    `python manage.py createsuperuser`
     You will not be able to log in via the front end straight away, instead you'll have to go to django admin and create a `user_state` object
    and link it to your newly created user account. Alternatively, you can create an account via a the frontend.





