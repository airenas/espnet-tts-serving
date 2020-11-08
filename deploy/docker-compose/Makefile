-include .env
#####################################################################################
start:
	docker-compose up -d

stop:
	docker-compose stop && docker-compose rm -f

clean: stop
#####################################################################################
test:
	curl -i -X POST http://localhost:8000/model -d '{"text":"o", "model":"aaaa"}'

test-file:
	curl -i -X POST http://localhost:8000/model -d@data.json