PYTHON := python3
TARGET := qr
TARGET_TMP := /tmp

WHEEL = $(shell ls -t dist/*.whl 2>/dev/null | head -n1)

build: clean
	$(PYTHON) -m build

# -----------------------
#   Local install
# -----------------------

install-local: build
	@echo "Installing locally..."
	sudo $(PYTHON) -m pip install $(WHEEL) --force-reinstall --prefix=/usr

uninstall-local: clean
	@echo "Uninstalling pciecap (if installed)..."
	-sudo $(PYTHON) -m pip uninstall -y pciecap

install-dir:
	@cd /tmp && python3 -c "import pciecap; print(pciecap.__file__)"

# -----------------------
#   Remote install
# -----------------------

scp: build
	@echo "Copying $(WHEEL) to $(TARGET)..."
	scp $(WHEEL) $(TARGET):$(TARGET_TMP)/

remote-install:
	@echo "Installing on $(TARGET)..."
	ssh $(TARGET) "python3 -m pip install --force-reinstall $(TARGET_TMP)/$(notdir $(WHEEL))"

deploy: scp remote-install
	@echo "Done."

clean:
	rm -rf build dist pciecap.egg-info

.PHONY: build install-local scp remote-install deploy clean
