#!/bin/bash

poetry install
poetry export -f requirements.txt -o requirements.txt --without-hashes
func host start