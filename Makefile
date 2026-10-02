.PHONY: setup seed train evaluate test run docker clean

setup:
	pip install -r requirements.txt

seed:
	python database/seed.py

train:
	python ml/train.py

evaluate:
	python ml/evaluate.py

test:
	python -m pytest tests/

run:
	python -m uvicorn app.main:app --host 127.0.0.1 --port 8085 --reload

docker:
	docker-compose up --build -d

clean:
	rm -rf __pycache__ .pytest_cache *.egg-info
