# clicoh

START PROJECT AT LOCALHOST:

    1. Install python on the computer in version > 3.9.5 (set the environment variable path as corresponse)
    2. (optional) Create virtual environment (./[Name of virtual environment]/Scripts/activate)
    3. Install all requirements (pip install -r requirements.txt)
    4. Install PostgreSQL and create a database named "clicoh" with pgAdmin and restore a backup from the file "backup"
    5. At folder "/clicoh" run "python manage.py makemigrations", "python manage.py migrate" and finally "python manage.py runserver"
    6. Open app at localhost:8000/

COMMAND update all Packages: pip freeze | %{$.split('==')[0]} | %{pip install --upgrade $}