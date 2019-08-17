#!/bin/bash
set -Eeuo pipefail

cd "$( dirname "${BASH_SOURCE[0]}" )"
! rm -rf gobgp_interface
mkdir -p gobgp_interface
pushd gobgp

# must first download at least protobuf packages
export GO111MODULE=on
go get -d ./...
PROTOBUF_BASEDIR="$(go list -f '{{ .Dir }}' -m github.com/golang/protobuf)"

# fix some problems
# https://github.com/osrg/gobgp/issues/2095#issuecomment-516404518
git reset --hard
for f in ../gobgp_patches/*.patch
do
	patch -p1 <"$f"
done

python3 -m grpc_tools.protoc -I./api -I"$PROTOBUF_BASEDIR"/ptypes --python_out=../gobgp_interface --grpc_python_out=../gobgp_interface api/gobgp.proto api/attribute.proto api/capability.proto
