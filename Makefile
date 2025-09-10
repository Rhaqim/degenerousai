.PHONY: build run run-build test

build:
	poetry lock
	poetry install

run:
	poetry run uvicorn src.degenerousai.main:app --host 0.0.0.0 --port 8000
# 	poetry run python src/degenerousai/main.py

run-build: build run

test:
	curl -X POST http://127.0.0.1:8000/api/v1/audio/speech -H "Content-Type: application/json" -d '{"input": "Oh sweet white, come let me eat you please. The rabbit tried to help Alice defeat the Queen of hearts but neither was successful. So they had to seek out the mad hatter to get the tools they required."}' --output hello.mp3