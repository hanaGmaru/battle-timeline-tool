ASSETS_DIR := $(CURDIR)/../frontend/src/assets
STATIC_DIR := $(CURDIR)/../frontend/static

.PNONY: all
all: clean scrape install

.PNONY: clean
clean:
	rm -rf dist
	mkdir -p dist/{img,data}
	mkdir -p $(STATIC_DIR)/{img,data}
	rm -rf $(STATIC_DIR)/img/skill_icon
	rm -f $(STATIC_DIR)/data/lang_text.*.json
	rm -f $(ASSETS_DIR)/skill_data.js

.PNONY: scrape
scrape:
	python web-scraper.py

.PNONY: install
install:
	cp dist/data/skill_data.js $(ASSETS_DIR)/
	cp dist/data/lang_text.*.json $(STATIC_DIR)/data/
	cp -r dist/img $(STATIC_DIR)/img/skill_icon
