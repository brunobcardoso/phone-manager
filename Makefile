.PHONY: clean coverage shellp test install admin run erd cerd

clean:
		find . -name "*.pyc" -delete
		find . -name "*.pyo" -delete
		rm -f .coverage
		rm -rf htmlcov

coverage: clean
		pipenv run pytest core/tests/ -s -v --cov=core --cov-branch --cov-report=term-missing --cov-report=html

shellp:
		pipenv run python manage.py shell_plus

test: clean
		pipenv run pytest -v -rf core/tests/

install:
		cp .env.example .env
		pipenv install --dev
		pipenv run python manage.py migrate
		pipenv run python manage.py runserver

admin:
		echo "from django.contrib.auth.models import User; \
		User.objects.filter(email='admin@email.com').delete(); \
		User.objects.create_superuser('admin', 'admin@email.com', 'pass')" | \
		pipenv run python manage.py shell

run:
		pipenv run python manage.py runserver

erd:
		pipenv run python manage.py graph_models core -o core_erd.png

cerd:
		pipenv run python manage.py graph_models -a -o complete_erd.png