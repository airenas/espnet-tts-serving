-include Makefile.options
MODEL_PATH?=./model
#####################################################################################
service=airenas/espnet-tts-serving
version=0.2
version-gpu=0.3
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
########### DOCKER GPU ##############################################################
tag-gpu=$(service)-gpu:$(version-gpu).$(commit_count)
dbuild-gpu: $(dist_dir)/$(executable_name)
	docker build -f Dockerfile_gpu -t $(tag-gpu) ./

dpush-gpu: dbuild-gpu
	docker push $(tag-gpu)
#####################################################################################
.PHONY:
	 dbuild dpush
