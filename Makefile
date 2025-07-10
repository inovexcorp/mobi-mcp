.PHONY: init

ENGINE := $(shell command -v podman > /dev/null 2>&1 && echo podman || echo docker)

init:
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment with Python 3.12..."; \
		python3.12 -m venv .venv; \
		echo "Virtual environment created successfully!"; \
	else \
		echo "Virtual environment already exists."; \
	fi

docker:
	$(ENGINE)  build -t mobi-mcp .

run_docker: docker
	$(ENGINE) run --rm --name mobi-mcp -p 8000:8000 mobi-mcp:latest