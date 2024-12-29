# Backend powering Nemo

<img src="https://iili.io/tSScHG.png" />

## Nemo:

https://nemo-landing-page.netlify.app/

## Tech

1. Python
2. FastAPI
3. Postgres Heroku for prod and Docker container for local setup.
4. Async database support using Async Sqlalchemy ORM.
5. Frontend (React) hosted on Netlify (https://nemo-app.netlify.app/)
6. Backend hosted on Heroku and DETA.

## Nemo

Nemo is your little helper and companion no matter if you need to focus, tune out other noises or if you want to have a moment of calm and relaxation.

LandingPage: https://nemo-landing-page.netlify.app/

Demo: https://nemo-app.netlify.app/

## Deployment

Heroku Deployment:
https://nemo-python.herokuapp.com/

DETA Deployment:
https://nemo.deta.dev/

AWS Deployment
https://jt5o8ghpdk.execute-api.us-east-1.amazonaws.com/

### Deploy to AWS

```docker build -t nemo-backend .```

```docker run -d -p 3000:3000 --name nemo-backend nemo-backend```

```docker cp <container_id>:/app/lambda_function.zip C:\Users\<user>\Documents\Projects\nemo-backend```

```cdk deploy --profile <your-profile>```
