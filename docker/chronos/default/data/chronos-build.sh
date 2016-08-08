#!/bin/bash

set -e

BUILD_DIR=/chronos-src
PACKAGING_DIR=/tmp/fpm-packaging
ASSEMBLY_WITH_TESTS=${ASSEMBLY_WITH_TESTS-false}

echo "Creating build directory..."

pushd ${BUILD_DIR} >/dev/null

if [ $ASSEMBLY_WITH_TESTS = true ]; then
  echo "[CHRONOS BUILD]: Assembling Chronos ${BUILD_CHRONOS_VERSION} with tests..."
  mvn package || exit 1000
else
  echo "[CHRONOS BUILD]: Assembling Chronos ${BUILD_CHRONOS_VERSION} without tests..."
  mvn package -DskipTests=true || exit 1000
fi

echo "[CHRONOS BUILD]: Creating FPM install directory..."
rm -rf ${PACKAGING_DIR}${INSTALL_DIRECTORY}
mkdir -p ${PACKAGING_DIR}${INSTALL_DIRECTORY}

echo "[CHRONOS BUILD]: Copying output..."
cp -R bin ${PACKAGING_DIR}${INSTALL_DIRECTORY}
cp -R target ${PACKAGING_DIR}${INSTALL_DIRECTORY}
echo ${BUILD_CHRONOS_VERSION} > ${PACKAGING_DIR}${INSTALL_DIRECTORY}/chronos.version

popd >/dev/null

# We do not package anything except marathon iteself.
# Any service or config needs to be provided after installation.

echo "[CHRONOS BUILD]: Preparing DEB package..."
fpm -s dir -t deb -n ${BUILD_CHRONOS_PACKAGE_NAME} -v ${FPM_OUTPUT_VERSION} -C ${PACKAGING_DIR}

echo "[CHRONOS BUILD]: Preparing RPM package..."
fpm -s dir -t rpm -n ${BUILD_CHRONOS_PACKAGE_NAME} -v ${FPM_OUTPUT_VERSION} -C ${PACKAGING_DIR}

echo "[CHRONOS BUILD]: Build ready..."

mkdir -p /output/${BUILD_CHRONOS_VERSION}
mv *.rpm /output/${BUILD_CHRONOS_VERSION}
mv *.deb /output/${BUILD_CHRONOS_VERSION}