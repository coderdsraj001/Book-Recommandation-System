Prerequisites(ubuntu)

Python: 
    Ensure Python 3.8 or higher is installed on your system. You can download it from python.org.

Virtual Environment: 
    Install virtualenv for managing Python environments:

Setup the Virtual Environment:
    python3 -m venv env_book_management 
                
Activate the virtual environment:
    source env_book_management/bin/activate

Install Dependencies:
    pip install -r requirements.txt

Run Migrations:
    python manage.py makemigrations
    python manage.py migrate

Start the Development Server
    python manage.py runserver

Now Test it usign postmen collection.




