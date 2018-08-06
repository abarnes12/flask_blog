#
# First Flask App Dockerfile
#
#

# Pull base image.
FROM centos:latest

ENV PATH /opt/conda/bin:$PATH

# Build commands
RUN yum swap -y fakesystemd systemd && \
    yum install -y systemd-devel
RUN yum install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1
RUN yum install -y python-setuptools mysql-connector-python mysql-devel gcc python-devel git vim gcc
RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh
    # Conda no longer likes the following lines
    #ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    #echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    #echo "conda activate base" >> ~/.bashrc
RUN mkdir /opt/flask_blog
WORKDIR /opt/flask_blog
ADD . /opt/flask_blog
RUN conda env create -n flaskdev -f /opt/flask_blog/venv/environment.yml

# Define working directory.
WORKDIR /opt/flask_blog

# Define default command.
# CMD ["python", "manage.py", "runserver"]
