#!/bin/bash
find -name *ipynb |grep -v venv | xargs ipython3 nbconvert --to script
