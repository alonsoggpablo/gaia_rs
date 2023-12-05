# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Update package lists and install system dependencies
RUN apt-get update && apt-get install -y \
  wget \
  bzip2 \
  binutils \
  libproj-dev \
  gdal-bin \
  libgdal-dev\
  cmake \
  g++ \
  unzip \
  sqlite3 \
  libsqlite3-dev \
  libtiff-dev \
  libcurl4-gnutls-dev \
  autoconf \
  libtool \
  libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal


# Install json-c
RUN wget https://s3.amazonaws.com/json-c_releases/releases/json-c-0.13.1.tar.gz && \
  tar xzf json-c-0.13.1.tar.gz && \
  cd json-c-0.13.1 && \
  ./configure && \
  make && \
  make install && \
  ldconfig

# 1.- Install GEOS
RUN wget https://download.osgeo.org/geos/geos-3.8.1.tar.bz2 && \
  tar xjf geos-3.8.1.tar.bz2 && \
  cd geos-3.8.1 && \
  mkdir build && \
  cd build && \
  cmake -DCMAKE_BUILD_TYPE=Release .. && \
  cmake --build . && \
  cmake --build . --target install && \
  ldconfig

# 2.- Install PROJ
RUN wget http://download.osgeo.org/proj/proj-8.0.0.tar.gz && \
    wget http://download.osgeo.org/proj/proj-datumgrid-1.8.zip && \
    tar xzf proj-8.0.0.tar.gz && \
    cd proj-8.0.0/data && \
    unzip ../../proj-datumgrid-1.8.zip && \
    cd ../.. && \
    cd proj-8.0.0 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . && \
    cmake --build . --target install && \
    ldconfig

# Install libgeotiff
RUN wget http://download.osgeo.org/geotiff/libgeotiff/libgeotiff-1.6.0.tar.gz && \
  tar xzf libgeotiff-1.6.0.tar.gz && \
  cd libgeotiff-1.6.0 && \
  ./configure && \
  make && \
  make install && \
  ldconfig

# Download GDAL
RUN wget http://download.osgeo.org/gdal/3.8.1/gdal-3.8.1.tar.gz

# Extract GDAL and install it
RUN tar xzf gdal-3.8.1.tar.gz && \
    cd gdal-3.8.1 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . && \
    cmake --build . --target install && \
    ldconfig

# Set GDAL and GEOS environment variables
ENV CPLUS_INCLUDE_PATH=/usr/local/include
ENV C_INCLUDE_PATH=/usr/local/include
ENV GEOS_LIBRARY_PATH=/usr/local/lib/libgeos_c.so
ENV GDAL_LIBRARY_PATH=/usr/local/lib/libgdal.so


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /gaia_rs

# Install dependencies
COPY requirements.txt /gaia_rs/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /gaia_rs/


COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf


