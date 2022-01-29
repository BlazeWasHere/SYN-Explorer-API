python := python3

tests:
	$(python) -m gevent.monkey --module pytest -vv

docker:
	docker-compose up --build -d

.PHONY: tests docker
