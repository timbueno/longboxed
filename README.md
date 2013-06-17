# Longboxed

Longboxed is dedicated to comic book lovers who just want an easy way to discover which comics are coming out each week. Never miss an important issue after a long hiatus.

Features:
- Each weeks comic releases, updated daily
- User customizable pull lists
- Google Calendar integration

Future features:
- Get recomendations from friends
- 'Follow' friends and their pull lists

## Installation notes for developers

1. Make sure 'pip' is installed.
    - 'sudo easy_install pip'
2. Install 'virtualenv' with 'pip'
    - 'sudo pip install virtualenv'
3. Inside 'longboxed' project root, install virtual environment
    - 'virtualenv venv --distribute'
4. Run the virtual environment
    - Make sure you are in the 'longboxed' project root
    - 'source venv/bin/activate'
    - The virtual environment should now be activated.
5. Install python dependencies from requirements file in virtual environment.
    - Make sure virtual environment is activated.
    - 'pip install -r requirements.txt'
    - All dependencies should install.

## Running Longboxed locally
1. Install according to installation instructions above.
2. Turn on virtual environment
    - 'source venv/bin/activate'
3. Run longboxed
    - 'python longboxed.py'