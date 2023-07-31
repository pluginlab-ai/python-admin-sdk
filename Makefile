all: build install

install:
	pip3 install ./dist/*.tar.gz

build: clean
	python3 setup.py sdist bdist_wheel
	
clean:
	rm -rf build dist

publish: clean build
	twine upload dist/*
