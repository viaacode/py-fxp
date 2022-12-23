.ONESHELL:
SHELL = /bin/bash

.PHONY: all test

test:
	echo Testing not implemented
build:
	docker build --no-cache . -t default-route-openshift-image-registry.meemoo2-2bc857e5f10eb63ab790a3a1d19a696c-i000.eu-de.containers.appdomain.cloud/tina/py-fxp:dev
push:
	docker push default-route-openshift-image-registry.meemoo2-2bc857e5f10eb63ab790a3a1d19a696c-i000.eu-de.containers.appdomain.cloud/tina/py-fxp:dev
deploy-dev:
	oc rollout restart deployment/py-fxp-dev
