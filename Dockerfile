FROM golang:1-buster as grpc_interface_builder
ARG DEBIAN_FRONTEND=noninteractive
ENV GOPATH=/root/go

RUN apt-get update -y \
    && apt-get install -y python3 python3-pip python3-setuptools
RUN pip3 install --upgrade grpcio-tools

COPY . /pilot
WORKDIR /pilot
RUN mkdir -p "$GOPATH" \
    && ./scripts/build_grpc.sh

FROM debian:buster-slim as gobgp_builder
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y \
    && apt-get install -y wget tar

WORKDIR /root
ARG GOBGP_DOWNLOAD_URL=https://github.com/osrg/gobgp/releases/download/v2.15.0/gobgp_2.15.0_linux_amd64.tar.gz
RUN wget ${GOBGP_DOWNLOAD_URL} -O gobgp.tar.gz \
    && tar -xvf gobgp.tar.gz

FROM python:3-buster
LABEL maintainer="docker@public.swineson.me"
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends supervisor curl \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY --from=gobgp_builder /root/gobgp /root/gobgpd /usr/local/bin/
RUN setcap CAP_NET_BIND_SERVICE=+eip /usr/local/bin/gobgpd

COPY . /tmp/pilot
COPY --from=grpc_interface_builder /pilot/pilot/gobgp_interface /tmp/pilot/pilot/gobgp_interface

RUN cd /tmp/pilot \
    && python3 setup.py install \
    && rm -rf /tmp/pilot \
    && setcap CAP_NET_BIND_SERVICE=+eip $(realpath $(which python))

COPY supervisor /etc/supervisor/
COPY config /etc/pilot/

EXPOSE 80/tcp
CMD [ "supervisord", "-c", "/etc/supervisor/supervisor.conf", "-n" ]

