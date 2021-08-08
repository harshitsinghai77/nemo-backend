install:
	poetry install

export_requirments:
	poetry export -f requirements.txt --output requirements.txt

deploy:
	git push heroku master

runserver:
	uvicorn main:app --reload

docker_image:
	docker build -t nemo-app .

start_docker_container:
	docker run -d --name nemo-app -p 5000:5000 nemo-app
  
format:
	bash format.sh
	
lint:
	pylint nemo

apache_benchmark:
	ab -c 100 -n 10000 http://127.0.0.1:8000/

molotov_benchmark:
	molotov -v -r 100 benchmark/molotov-benchmark.py
