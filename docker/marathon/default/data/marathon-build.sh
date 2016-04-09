#!/bin/bash

set -e

BUILD_DIR=/marathon-src
PACKAGING_DIR=/tmp/marathon-packaging
ASSEMBLY_WITH_TESTS=${ASSEMBLY_WITH_TESTS-false}
INCLUDE_HAPROXY_MARATHON_BRIDGE=${INCLUDE_HAPROXY_MARATHON_BRIDGE-true}

echo "Creating build directory..."

pushd ${BUILD_DIR} >/dev/null

if [ $ASSEMBLY_WITH_TESTS = true ]; then
  echo "[MARATHON BUILD]: Assembling Marathon ${BUILD_MARATHON_VERSION} with tests..."
  sbt assembly || exit 1000
else
  echo "[MARATHON BUILD]: Assembling Marathon ${BUILD_MARATHON_VERSION} without tests..."
  sbt "set test in Test := {}" assembly || exit 1000
fi

echo "[MARATHON BUILD]: Creating FPM install directory..."
rm -rf ${PACKAGING_DIR}${INSTALL_DIRECTORY}
mkdir -p ${PACKAGING_DIR}${INSTALL_DIRECTORY}/target

echo "[MARATHON BUILD]: Copying output..."
cp -R bin ${PACKAGING_DIR}${INSTALL_DIRECTORY}
cp -R target/scala-2* ${PACKAGING_DIR}${INSTALL_DIRECTORY}/target

if [ $INCLUDE_HAPROXY_MARATHON_BRIDGE = true ]; then
  echo "Including haproxy-marathon-bridge in this build..."
  cp examples/haproxy-marathon-bridge ${PACKAGING_DIR}${INSTALL_DIRECTORY}/bin/
  chmod +x ${PACKAGING_DIR}${INSTALL_DIRECTORY}/bin/haproxy-marathon-bridge
fi

popd >/dev/null

# We do not package anything except marathon iteself.
# Any service or config needs to be provided after installation.

echo "[MARATHON BUILD]: Preparing DEB package..."
fpm -s dir -t deb -n ${BUILD_MARATHON_PACKAGE_NAME} -v ${FPM_OUTPUT_VERSION} -C ${PACKAGING_DIR}

echo "[MARATHON BUILD]: Preparing RPM package..."
fpm -s dir -t rpm -n ${BUILD_MARATHON_PACKAGE_NAME} -v ${FPM_OUTPUT_VERSION} -C ${PACKAGING_DIR}

echo "[MARATHON BUILD]: Build ready..."
mkdir -p /output/${BUILD_MARATHON_VERSION}
mv ${BUILD_DIR}/*.rpm /output/${BUILD_MARATHON_VERSION}
mv ${BUILD_DIR}/*.deb /output/${BUILD_MARATHON_VERSION}