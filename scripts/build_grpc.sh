#!/bin/bash
set -Eeuo pipefail

BUILD_DST="pilot/gobgp_interface"

cd "$( dirname "${BASH_SOURCE[0]}" )"/..

python3 -m pip install --user -r scripts/grpc-build-requirements.txt

! rm -rf "${BUILD_DST}"/*.py
mkdir -p "${BUILD_DST}"
pushd gobgp

# must first download at least protobuf packages
export GO111MODULE=off
go get -u ./...
PROTOBUF_BASEDIR="$(go list -f '{{ .Dir }}' -m github.com/golang/protobuf)"

git reset --hard

# fix some problems
# https://github.com/osrg/gobgp/issues/2095#issuecomment-516404518
for f in ../gobgp_patches/*.patch
do
	echo "Applying patch $f..."
	patch -R -p1 <"$f"
done

echo "Building GRPC interfaces..."
python3 -m grpc_tools.protoc -I./api -I"$PROTOBUF_BASEDIR"/ptypes --python_out=../"${BUILD_DST}" --grpc_python_out=../"${BUILD_DST}" api/gobgp.proto api/attribute.proto api/capability.proto

git reset --hard
popd
