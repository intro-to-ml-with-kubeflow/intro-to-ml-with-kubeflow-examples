# Since we used Jupyter notebooks to do the first pass extraction, we can try directly use that notebook with
# Kubeflow's pre-baked "tensorflow-notebook-image" (based on the Jupyter image) that automatically
# launches the notebooks included in the docker file. If you have multiple notebooks
# Give them names like:
# 01-mything.ipynb
# 02-step2.ipynb
# as they will be executed in lexiographical order.
FROM gcr.io/kubeflow-images-public/tensorflow-1.6.0-notebook-cpu
RUN pip install ktext==0.34

COPY ./ /workdir /

