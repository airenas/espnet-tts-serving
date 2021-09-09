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
prepare-env:
	conda create -y -n esp-$(DEVICE) python=3.6.12
drop-env:
	conda remove --name esp-$(DEVICE) --all
install-req:
	pip install numpy==1.19.4
ifeq ($(DEVICE),cpu)
	pip install torch==1.7.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
	pip install -r requirements.txt
	pip install -r requirements_cpu.txt
else
	pip install -r requirements.txt
	pip install -r requirements_gpu.txt
endif

run:
	CONFIG_FILE=$(CONFIG_FILE) DEVICE=$(DEVICE) PORT=$(PORT) WORKERS=$(WORKERS) python run.py
########### SERVICE#################################################################
logs:
	mkdir -p $@
install-service: deploy/service/espnet.service | logs
	cp deploy/service/espnet.service /etc/systemd/system/
	systemctl enable espnet.service
uninstall-service:
	systemctl disable espnet.service
	rm -f /etc/systemd/system/espnet.service
deploy/service/espnet.service: deploy/service/espnet.service.in
	cat $< | envsubst > $@
run-service:
	. ~/miniconda3/etc/profile.d/conda.sh; conda activate esp-$(DEVICE); \
		MODEL_ZIP_PATH=$(MODEL_ZIP_PATH) DEVICE=$(DEVICE) PORT=$(PORT) python run.py
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
