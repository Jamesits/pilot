FROM golang:1-buster as grpc_interface_builder

RUN apt-get update -y \
    && apt-get install -y python3 python3-pip python3-setuptools

COPY . /pilot
WORKDIR /pilot
RUN ./scripts/build_grpc.sh

FROM python:3-buster
LABEL maintainer="docker@public.swineson.me"

COPY . /tmp/pilot
COPY --from=grpc_interface_builder /pilot/pilot/gobgp_interface /tmp/pilot/pilot/gobgp_interface

RUN cd /tmp/pilot \
    && python3 setup.py install \
    && cd \
    && rm -r /tmp/pilot

CMD [ "pilot_server" ]
