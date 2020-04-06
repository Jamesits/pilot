#!/bin/bash
set -Eeuo pipefail
set +x

BUILD_DST="pilot/gobgp_interface"

cd "$( dirname "${BASH_SOURCE[0]}" )"/..
BUILD_DST=$(realpath "${BUILD_DST}")

# install grpc tools
python3 -m pip install --user -r scripts/grpc-build-requirements.txt

! rm -rf "${BUILD_DST}"/*.py
mkdir -p "${BUILD_DST}"
pushd gobgp

# must first download at least protobuf packages
export GO111MODULE=on
go get -u -d ./...
PROTOBUF_BASEDIR="$(go list -f '{{ .Dir }}' -m github.com/golang/protobuf)"

echo "Building GRPC interfaces..."
python3 -m grpc_tools.protoc -I./api -I"$PROTOBUF_BASEDIR"/ptypes --python_out="${BUILD_DST}" --grpc_python_out="${BUILD_DST}" api/*.proto

