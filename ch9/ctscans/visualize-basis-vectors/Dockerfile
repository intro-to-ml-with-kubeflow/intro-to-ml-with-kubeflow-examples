FROM python:3-buster

RUN pip install numpy
RUN pip install matplotlib
RUN pip install google-cloud-storage
COPY src/program.py /program.py

CMD ["python" , "/program.py"]