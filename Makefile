void:
	docker compose up -d

d:
	docker ps
	@docker exec -it void_django bash

w:
	docker ps
	@docker exec -it void_worker bash

again:
	docker compose restart

it_stop:
	docker compose rm -safv

images:
	docker compose up --build -d

db:
	python /code/django/manage.py makemigrations
	@python /code/django/manage.py migrate