# pythonify
> **Pythonify** is an practice problem tracker web application developed by **Shrish Mohapatra** using the **Django** framework. Key features include an authentication system with varying levels of access, ability to create/edit practice problems & sets, and various other features.

![alt text](https://github.com/theRealShrishM/pythonify/blob/master/img/pythonify_problems.jpg "Practice Problems")

## Running Project
You will first need to clone the repository to your local machine:
```
git clone https://github.com/theRealShrishM/pythonify.git
```

Then you will need to install the following via pip (ensure you have Python 3.7.X installed):
```
pip install django
pip install django-crispy-forms
```

After, you will need to navigate to the repository via command line/terminal:
```
cd pythonify-master
```

Here, you will run the server:

Windows: `python manage.py runserver`

Linux/Mac: `python3 manage.py runserver`

Go to your browser and type the following: **127.0.0.1:8000**

## Using the Application
The document **Pythonify Project Report.pdf** explains the features of the application in exhaustive detail. Feel free to refer to this document as needed.

You will however need to login as an admin to be able to fully use the application. A demo admin account has been made with the username **admin** and the password **pythonify**.
Be sure to change the password before deploying the application!
