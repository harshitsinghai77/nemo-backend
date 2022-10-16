install:
	poetry install

add_pafy_to_requirements:
	bash add_library.sh

export_requirments:
	poetry export --without-hashes -f requirements.txt --output requirements.txt && make add_pafy_to_requirements

deploy-heroku:
	make export_requirments && git push heroku master

deploy-deta:
	pytest && make add_pafy_to_requirements && deta deploy

deploy:
	make deploy-deta

start-server:
	code . && uvicorn main:app --reload

new-tab:
	gnome-terminal --tab -e "bash -c 'cd ../../frontend/nemo/ && code . && npm start'" && make start-server

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

remove_pycache:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
