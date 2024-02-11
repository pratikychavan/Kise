FROM python:3.10
ARG access_key
ARG secret_key
ARG region
ARG server
ENV server=${server}
RUN apt-get update && apt-get upgrade -y
RUN apt-get install sudo make -y
COPY . /code
WORKDIR /code/${server}
RUN pip install -r /code/${server}/requirements.txt
RUN chmod 777 /code/script.sh /code/credentials.sh
RUN /code/credentials.sh
ENTRYPOINT [ "/bin/bash", "/code/script.sh" ]
CMD [ "${server}" ]