.PHONY: setup selfcheck run test sweep figures tables clean

setup:        ## install dependencies
	pip install -r requirements.txt

selfcheck:    ## verify the model reproduces the brief table
	python model.py --selfcheck

run:          ## print break-even + Monte-Carlo summary with current params
	python model.py

test:         ## run the test suite
	pytest -q

sweep:        ## TODO (next block): parameter sweep -> CSV
	@echo "TODO (bloc suivant): balayage (I_grid x mass x lifetime x accounting) -> CSV"

figures:      ## TODO (next block): break-even map + tornado
	@echo "TODO (bloc suivant): carte de break-even (2 contours provenance) + tornado -> figures/"

tables:       ## TODO (next block): threshold tables
	@echo "TODO (bloc suivant): tables des seuils -> tables/"

clean:
	rm -rf __pycache__ .pytest_cache .ipynb_checkpoints
