#!/bin/bash
set -e

python3 create_publications.py
mkdir -p ../_bibtex ../_pages
mv *.html ../_bibtex
mv publications.md ../_pages
