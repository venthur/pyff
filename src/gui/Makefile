PYUIC = pyuic4

all:
	for i in $(shell find *.ui); do \
		$(PYUIC) --output=$$(basename $$i .ui).py $$i; \
	done

