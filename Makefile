.PHONY: run test
run:
	poetry run python src/degenerousai/main.py

test:
	curl -X POST http://127.0.0.1:8000/api/v1/audio/speech -H "Content-Type: application/json" -d '{"input": "The rabbit tried to help Alice defeat the Queen of hearts but neither was successful. So they had to seek out the mad hatter to get the tools they required."}' --output hello.mp3