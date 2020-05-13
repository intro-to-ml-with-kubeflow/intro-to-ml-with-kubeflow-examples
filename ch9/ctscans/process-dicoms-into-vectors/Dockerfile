FROM pydicom/dicom:v3.6.5

# From https://github.com/HealthplusAI/python3-gdcm
RUN apt update && apt install -y python-vtk6 libvtk6-dev cmake-curses-gui swig python3-dev libpython3.7-dev
## checkinstall missing...
RUN ln -s /opt/conda/bin/* /usr/local/bin
RUN git clone --branch release git://git.code.sf.net/p/gdcm/gdcm
RUN mkdir build
RUN cd build && cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_C_FLAGS=-fPIC -D CMAKE_CXX_FLAGS=-fPIC -D GDCM_BUILD_SHARED_LIBS:BOOL=ON \
    -D GDCM_WRAP_PYTHON=ON -D PYTHON_EXECUTABLE=/usr/local/bin/python3.7 \
    -D PYTHON_INCLUDE_DIR=/usr/include/python3.7m/ -D GDCM_BUILD_SHARED_LIBS=ON -D GDCM_USE_VTK=ON ../gdcm
## They forgot this line in instuctions, but is important...
RUN cd build && make install
# checkinstall -D -y --pkgversion --pkgname=python3-gdcm --pkgversion=1  # checkinstall doesn't exist in debian?
RUN cp /usr/local/lib/gdcm.py /opt/conda/lib/python3.7/site-packages/
RUN cp /usr/local/lib/gdcmswig.py /opt/conda/lib/python3.7/site-packages/
RUN cp /usr/local/lib/_gdcmswig.so /opt/conda/lib/python3.7/site-packages/
RUN cp /usr/local/lib/libgdcm* /opt/conda/lib/python3.7/site-packages/
RUN ldconfig

# RUN mkdir /data already exists in base
# todo move these to requirements.txt
RUN pip install numpy
RUN pip install scipy
RUN pip install google-cloud-storage

ENV GOOGLE_APPLICATION_CREDENTIALS="/secret/gcp-credentials/user-gcp-sa.json"
COPY src/program.py /program.py
