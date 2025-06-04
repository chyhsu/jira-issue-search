FROM quay.io/rockylinux/rockylinux:9-minimal

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install build tools and dependencies for SQLite
RUN microdnf install -y gcc make wget tar gzip python3.12 python3.12-pip --nodocs --setopt=install_weak_deps=0
RUN microdnf update -y && microdnf clean all

# Download and install zlib 1.3.1
RUN wget https://zlib.net/zlib-1.3.1.tar.gz && \
    tar -xzf zlib-1.3.1.tar.gz && \
    cd zlib-1.3.1 && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    cd .. && \
    rm -rf zlib-1.3.1* && \
    ldconfig

# Download and install SQLite >= 3.35.0 (e.g., 3.39.0)
RUN wget https://www.sqlite.org/2022/sqlite-autoconf-3390000.tar.gz && \
    tar -xzf sqlite-autoconf-3390000.tar.gz && \
    cd sqlite-autoconf-3390000 && \
    ./configure && \
    make && \
    make install && \
    cd .. && \
    rm -rf sqlite-autoconf-3390000* && \
    ldconfig


# Set LD_LIBRARY_PATH to include custom SQLite
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

WORKDIR /home/qnap

# Copy requirements first to leverage Docker cache
COPY res/requirements.txt ./res/

# Install Python dependencies
RUN python3.12 -m pip install --no-cache-dir -r res/requirements.txt

# Copy application code with proper structure
COPY run.py ./
COPY api ./api/
COPY util ./util/
COPY scheme ./scheme/
COPY db ./db/
COPY models ./models/

RUN mkdir -p /chroma_data

# Add group and user
RUN groupadd -g 101 qnap || true
RUN useradd -u 100 -g 101 -m -s /bin/bash qnap || true
RUN chown -R qnap:qnap /home/qnap /chroma_data

USER qnap

EXPOSE 8080
CMD ["python3.12", "run.py"]