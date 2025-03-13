run-api:
	. .env && python run.py

build-api-docker:
	docker build -t issue_search:latest -f res/docker/api.Dockerfile .

run-api-docker:
	docker rm -f issue_search_api
	docker run --name issue_search_api --rm --env-file .env --sig-proxy -p 8080:8080 issue_search
