#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(cd $CUR_DIR/..; pwd)

BOARD=orangepizero2

cd $TOP_DIR

DATETIME=$(date +'%Y-%m-%dT%H:%M:%SZ')
GIT_VERSION=$(git describe --tags --always)
GIT_COMMIT=$(git rev-parse HEAD | cut -c 1-7)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GIT_NUMBER=$(git rev-list HEAD | wc -l | awk '{print $1}')

VER_MAJOR_NUM=1
VER_MINOR_NUM=0
APP_VERSION=${VER_MAJOR_NUM}.${VER_MINOR_NUM}.${GIT_NUMBER}

FORCE=false
SETUP=true
if [[ x$1 == 1 ]]
then
    FORCE=true
fi
APP_VERSION=99.99.99
echo -n "${APP_VERSION}" > $TOP_DIR/version.txt

chmod +x $TOP_DIR/board/${BOARD}/bin/* -R
chmod +x $TOP_DIR/scripts/* -R

mkdir -p .ota

zip -r .ota/update_${APP_VERSION}.zip *  -x@.zipignore
MD5=`md5sum .ota/update_${APP_VERSION}.zip | cut -c1-32`

cat > .ota/version_info.json <<EOF
{
    "version": "${APP_VERSION}",
    "datetime": "${DATETIME}",
    "compatible": true,
    "url": "http://aiot.hzcsdata.com:30082/update_${APP_VERSION}.zip",
    "force": ${FORCE},
    "md5": "${MD5}",
    "execsetup": ${SETUP},
    "content": "This is the ota update zip content",
    "git_version": "${GIT_VERSION}",
    "git_commit": "${GIT_COMMIT}",
    "git_branch": "${GIT_BRANCH}"
}
EOF

echo "scp .ota/update_${APP_VERSION}.zip k8-storage:/data/nginx/www"
echo "scp .ota/version_info.json k8-storage:/data/nginx/www"
echo "cat .ota/version_info.json | jq -c"
