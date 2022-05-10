.PHONY: black
black:
	black -l 80 *.py
	black -l 80 courses/*.py
	black -l 80 results/*.py
	black -l 80 sessions/*.py
	black -l 80 index/*.py
	black -l 80 students/*.py
	black -l 80 programs/*.py

.PHONY: clean
clean:
	find . -type f -name "*.pyc" | xargs rm -rf
	find . -type d -name __pycache__ | xargs rm -rf