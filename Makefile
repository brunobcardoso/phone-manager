.PHONY: clean coverage shellp test

clean:
		find . -name "*.pyc" -delete
		find . -name "*.pyo" -delete
		rm -f .coverage
		rm -rf htmlcov

coverage: clean
		pytest core/tests/ -s -v --cov=core --cov-branch --cov-report=term-missing --cov-report=html

shellp:
		python manage.py shell_plus

test: clean
		pytest -v -rf core/tests/
