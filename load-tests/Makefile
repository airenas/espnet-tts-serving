DOCKER_IP=$(shell echo $$(ip addr show docker0 | grep -Po 'inet \K[\d.]+'))

vu?=50
req?=2000
voices?=2
data_dir?=$(CURDIR)
url?=http://localhost:8000

#################################################################################################
bin:
	mkdir -p $@
install-k6: bin/.k6.done
bin/k6-v0.34.0-linux-amd64.tar.gz: | bin
	wget -O $@_ https://github.com/grafana/k6/releases/download/v0.34.0/k6-v0.34.0-linux-amd64.tar.gz
	mv $@_ $@
bin/k6: bin/k6-v0.34.0-linux-amd64.tar.gz | bin
	tar xf $< -C bin
	mv bin/k6-v0.34.0-linux-amd64/k6 $@
	chmod +x $@
	touch $@
bin/.k6.done: bin/k6
install: bin/.k6.done
#################################################################################################
info:
	@echo IP: $(DOCKER_IP)

load: info bin/.k6.done
	VOICES_NUM=$(voices) URL=$(url)/model DATA_DIR=$(data_dir) ./bin/k6 run --vus $(vu) --iterations $(req) load.js

load-live: info
	URL=$(url)/live ./bin/k6 run --vus $(vu) --iterations $(req) load_live.js
#################################################################################################
dload: info
	docker run --add-host=host.docker.internal:$(DOCKER_IP) \
		--env VOICES_NUM=$(voices) \
		--env DATA_DIR=/data \
		--env URL=http://host.docker.internal:8000/model \
		-v  $(CURDIR)/data.json:/data/data.json:ro \
	    -i loadimpact/k6 run --vus $(vu) --iterations $(req) - < load.js

dload-live: info
	docker run --add-host=host.docker.internal:$(DOCKER_IP) \
		--env URL=http://host.docker.internal:8000/live \
		-i loadimpact/k6 run --vus $(vu) --iterations $(req) - < load_live.js

#################################################################################################
clean:
	rm -rf bin

all: load

.PHONY: load load-live
