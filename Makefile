requirments:
	poetry export -f requirements.txt --output requirements.txt

deploy:
	git push heroku master

rundev:
	uvicorn main:app --reload