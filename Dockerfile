FROM python:3.8

RUN pip install pipenv

WORKDIR /usr/src/app

COPY src/ ./
#RUN pipenv install --system --deploy --ignore-pipfile
RUN pipenv install --deploy --ignore-pipfile

CMD [ "pipenv", "run", "start" ]
