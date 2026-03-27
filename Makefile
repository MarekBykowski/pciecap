PYTHON := python3
PYTHONPATH := $(shell $(PYTHON) -c "import site; print(site.getusersitepackages())")

all: build

build: clean
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m build

scp: build
	scp dist/*.whl qr:/tmp/
	@echo -e "Install on the target with:\n\t pip3 install --force-reinstall /tmp/pciecap-0.1.0-py3-none-any.whl"
	@echo -e "Check what got installed:\n\t python3 -c \"import pciecap; print(pciecap.__file__)\""

install-local:
	$(PYTHON) -m pip install .

clean:
	rm -rf build dist pciecap.egg-info

.PHONY: all build clear
