-include Makefile.options
MODEL_PATH?=./model
#####################################################################################
service=airenas/espnet-tts-serving
version=0.1
commit_count=$(shell git rev-list --count HEAD)
#####################################################################################
test:
	pytest
run:
	MODEL_PATH=$(MODEL_PATH) python run.py
########### DOCKER ##################################################################
tag=$(service):$(version).$(commit_count)
dbuild: $(dist_dir)/$(executable_name)
	docker build -t $(tag) ./

dpush: dbuild
	docker push $(tag)
#####################################################################################
.PHONY:
	 dbuild dpush
