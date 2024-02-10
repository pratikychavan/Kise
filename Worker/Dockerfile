FROM python:3.10
ARG access_key
ARG secret_key
ARG region
RUN apt-get update && apt-get upgrade -y
COPY . /code
WORKDIR /code
RUN pip install -r /code/Worker/requirements.txt
RUN aws configure set aws_access_key_id $access_key \
    && aws configure set aws_secret_access_key $secret_key \
    && aws configure set default.region $region \
    && aws configure set default.output json
CMD [ "/usr/local/bin/python", "/code/Worker/worker.py" ]