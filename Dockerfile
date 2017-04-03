FROM python:2.7-alpine

RUN pip install virtualenv paver
ADD .
RUN virtualenv venv
RUN source venv/bin/activate
RUN pip install -r requirements-development.txt
RUN paver develop
RUN paver test
