-include Makefile.options
MODEL_PATH?=./model
#####################################################################################
service=airenas/espnet-tts-serving
version=0.3
version-gpu=0.4
commit_count=$(shell git rev-list --count HEAD)
torch_version=1.13.1
#####################################################################################
test/unit:
	pytest -vv

test/lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
prepare-env:
	conda create -y -n esp-$(DEVICE) python=3.7
drop-env:
	conda remove --name esp-$(DEVICE) --all
install-req:
# 	pip install numpy==1.19.4
ifeq ($(DEVICE),cpu)
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
		CONFIG_FILE=$(CONFIG_FILE) DEVICE=$(DEVICE) PORT=$(PORT) WORKERS=$(WORKERS) python run.py
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
########### GIT TAG #################################################################
git-tag:
	git tag "v$(version-gpu).$(commit_count)"
git-push-tag:
	git push origin --tags
#####################################################################################
.PHONY:
	 dbuild dpush
