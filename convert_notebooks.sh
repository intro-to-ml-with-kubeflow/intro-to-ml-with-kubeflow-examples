#!/bin/bash
find . -name "*ipynb" |grep -v venv | xargs -d '\n' ipython3 nbconvert --to script
