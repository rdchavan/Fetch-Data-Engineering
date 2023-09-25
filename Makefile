.PHONY: list
list:
	@echo "Available options:"
	@echo "  make check-python		- Test if python3 is available"
	@echo "  make check-docker		- Test if docker is available"
	@echo "  make check-docker-compose	- Test if docker-compose is available"
	@echo "  make install-dependencies		- Install all python application dependencies"
	@echo "  make docker-start		- Start the docker image localstack and postgres"
	@echo "  make docker-stop		- Stop the docker image localstack and postgres"
	@echo "  make docker-clean		- Prune unused docker image"
	@echo "  make python_etl_start		- Start the python application to push data from SQS to postgres "
	@echo "  make python_decrypt_start	- Query and decrypt the pushed data to stdout"
	@echo "  make clean			- Clear all the output"




.PHONY: check-python

check-python:
	@python3 -c "import sys" 2>/dev/null && echo "\nPython3 is installed" || echo "\nPython3 is not installed please install it first."

.PHONY: check-docker

check-docker:
	@docker --version 2>/dev/null && echo "\nDocker is installed" || echo "\nDocker is not installed please install it first"

.PHONY: check-docker-compose

check-docker-compose:
	@docker-compose --version 2>/dev/null && echo "\nDocker-compose is installed" || echo "\nDocker is not installed please install it first"

.PHONY: dependencies
install-dependencies:
	pip3 install -r requirements.txt

.PHONY: docker
docker-start:
	docker-compose -f Fetch.yml up -d
docker-stop:
	docker-compose -f Fetch.yml down
docker-clean:
	docker system prune -f

.PHONY: python3
python_etl_start :
	python3 Fetch_DE_ETL.py
python_decrypt_start :
	python3 Decrypt_App.py

.PHONY: clean
clean:
	@clear



