.PHONY: run test
run:
	poetry run python src/degenerousai/main.py

test:
	curl -X POST http://127.0.0.1:8000/api/v1/audio/speech -H "Content-Type: application/json" -d '{"input": "hello Mr man, how are you doing"}' --output hello.wav