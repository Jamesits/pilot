FROM golang:1-buster as grpc_interface_builder
ENV GOPATH=/root/go

RUN apt-get update -y \
    && apt-get install -y python3 python3-pip python3-setuptools
RUN pip3 install --upgrade grpcio-tools

COPY . /pilot
WORKDIR /pilot
RUN mkdir -p "$GOPATH" \
    && ./scripts/build_grpc.sh

FROM python:3-buster
LABEL maintainer="docker@public.swineson.me"

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends supervisor curl \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY . /tmp/pilot
COPY --from=grpc_interface_builder /pilot/pilot/gobgp_interface /tmp/pilot/pilot/gobgp_interface

RUN cd /tmp/pilot \
    && python3 setup.py install \
    && cd \
    && rm -r /tmp/pilot

COPY supervisor /etc/supervisor/
COPY config /etc/pilot/

EXPOSE 80/tcp
CMD [ "supervisord", "-c", "/etc/supervisor/supervisor.conf", "-n" ]

