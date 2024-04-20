#!/bin/bash

python3 create_publications.py
mv *.html ../_bibtex
mv publications.md ../_pages
