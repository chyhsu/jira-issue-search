run-api:
	. .env && python run.py

build-api-docker:
	docker build -t issue_search:latest -f res/docker/api.Dockerfile .

run-api-docker:
	docker rm -f issue_search_api
	docker run --name issue_search_api --rm --env-file .env --sig-proxy -p 8080:8080 issue_search
external-srv:
	nats-server -js > /dev/null 2>&1 &
	kubectl -n q2 port-forward ollama-7c8f77c44f-gttts 11434:11434 > /dev/null 2>&1 &

clean-external-srv:
	kill `ps | grep 'nats-server -js' | grep -v grep | awk '{print $$1}'` > /dev/null 2>&1 &
	kill `ps | grep 'kubectl -n q2 port-forward ollama-7c8f77c44f-gttts 11434:11434' | grep -v grep | awk '{print $$1}'` > /dev/null 2>&1 &