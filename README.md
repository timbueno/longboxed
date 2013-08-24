# Longboxed

Longboxed is dedicated to comic book lovers who just want an easy way to discover which comics are coming out each week. Never miss an important issue after a long hiatus.

Features:
- Each weeks comic releases, updated daily
- User customizable pull lists
- Google Calendar integration

Future features:
- Get recomendations from friends
- 'Follow' friends and their pull lists
- Get weekly emails of your pull list

## Installation notes for developers

Follow the instructions located in the project wiki:
- [Setting up a development environment](https://github.com/timbueno/longboxed/wiki/Setting-up-a-development-environment)

## Working on the project

Once you have set up the developer environment described above, working on the project is as simple as:

1. `vagrant up`
2. `vagrant ssh`
3. `workon longboxed`
4. `cd /vagrant`
5. `python wsgi.py`

When you are finished working for the day:

1. Exit the SSH session
2. `vagrant halt`
