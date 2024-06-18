# variables
PYTHON = python3
PIP = $(PYTHON) -m pip
REQUIREMENTS = requirements.txt
VENV = aclite
ACTIVATE = source $(VENV)/bin/activate

# Default target: install packages
.PHONY: all install clean

all: install

install: $(VENV)/bin/activate
	@echo "Installing Python packages in virtual environment: $(VENV)..."
	$(ACTIVATE) && $(PIP) install -r $(REQUIREMENTS)

$(VENV)/bin/activate: $(VENV)
	@echo "Creating virtual environment in directory: $(VENV)..."
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && $(PIP) install --upgrade pip

clean:
	@echo "Cleaning up..."
	$(PIP) uninstall -y -r $(REQUIREMENTS)
	@echo "Removing virtual environment: $(VENV)..."
	rm -rf $(VENV)
