install:
	poetry install

export_requirments:
	poetry export -f requirements.txt --output requirements.txt

deploy:
	git push heroku master

runserver:
	uvicorn main:app --reload

docker_image:
	docker build -t noiist-app .

start_docker_container:
	docker run -d --name noiist-app -p 5000:5000 noiist-app
  
format:
	bash format.sh
	
lint:
	pylint noiist