DOCKER_IP=$(shell echo $$(ip addr show docker0 | grep -Po 'inet \K[\d.]+'))

vu?=3
req?=20
voices?=2

info:
	@echo IP: $(DOCKER_IP)

load: info
	docker run --add-host=host.docker.internal:$(DOCKER_IP) \
		--env VOICES_NUM=$(voices) \
		-v  $(CURDIR)/data.json:/data/data.json:ro \
	    -i loadimpact/k6 run --vus $(vu) --iterations $(req) - < load.js

all: load

.PHONY:
	load