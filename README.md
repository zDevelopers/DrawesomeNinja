# DrawesomeNinja

DrawesomeNinja aims to offer an online draw-and-guess game (like Pictionary) as simple, beautiful and straighforward as possible, without neither Flash, Silverlight…, nor any required account.

It uses Python 3.6+, Django 1.11, and Django-Channels for websockets support.

_Currently in development._

## Development installation

Clone this repository into a directory and `cd` into it. Then, with Python 3.6 installed on the system:

```bash
# Install Pipenv
$ pip install --user pipenv

# Install all the project's dependencies
# This will also create the virtualenv for the project
$ pipenv install

# Enter the virtualenv
$ pipenv shell

# Run migrations to build the database schema
$ python manage.py migrate

# Start Django/Channels' development server
$ python manage.py runserver
```

You can check out [the Pipenv documentation](https://docs.pipenv.org/) for more details.

## Production deployment

See [Django-Channels' deployment documentation](https://channels.readthedocs.io/en/stable/deploying.html).