# gunicorn main:app --workers 2 --bind 0.0.0.0:5000 -k uvicorn.workers.UvicornWorker
uvicorn main:app --host 0.0.0.0 --port 5000