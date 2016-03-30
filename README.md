# Build Mesos locally

Build Mesos for any supported platform locally, with Docker *.
This program is a wrapper for the fantastic [mesos-deb-packaging](https://github.com/mesosphere/mesos-deb-packaging).

## Installation

Clone, make sure you have Docker and Git installed and working. You are ready to go.
This program uses Docker via command line and it works perfectly fine with Docker Toolbox.

    git clone https://github.com/radekg/mesos-toolbox.git
    export PATH=$PATH:`pwd`/mesos-toolbox

## * Supported target operating systems

- `Centos 7.1`
- `Debian Jessie`
- `Fedora 21`
- `Fedora 22`
- `Fedora 23`
- `Ubuntu Precise`
- `Ubuntu Trusty`

**More to come soon...**

## Commands

Below is the documentation of all available commands.

### build

To build an arbitrary tagged version:

    $> mesos-toolbox.py build --mesos-version 0.27.2 --os ubuntu:precise

To build from master branch:

    $> mesos-toolbox.py build --mesos-version master --os ubuntu:precise

To build from arbitrary commit sha:
    
    $> SHA=...
    $> mesos-toolbox.py build --mesos-master-branch $SHA --mesos-version $SHA --os debian:jessie

To use an alternative repository:

    $> mesos-toolbox.py build --mesos-version 0.28.0-rc2 --os debian:jessie --mesos-git-repository https://github.com/<username>/mesos-fork.git

### show-releases

This command is going to list available tags for a given repository.

    $> mesos-toolbox.py show-releases
    INFO:mesos-toolbox.py:Updating sources for https://github.com/apache/mesos.git...
    INFO:mesos-toolbox.py:Done.
    INFO:mesos-toolbox.py:Releases:
    0.10.0
    0.11.0
    ...

To use an alternative repository:

    $> mesos-toolbox.py show-releases --mesos-git-repository https://github.com/<username>/mesos-fork.git
    INFO:mesos-toolbox.py:Updating sources for https://github.com/<username>/mesos-fork.git...
    INFO:mesos-toolbox.py:Done.
    INFO:mesos-toolbox.py:Releases:
    0.10.0
    0.11.0
    ...

### show-builds

List builds stored locally:

    $> mesos-toolbox.py show-builds
    0.27.2-debian-jessie
    0.27.2-ubuntu-trusty
    ...

### remove-build

Remove a local build.

    $> mesos-toolbox.py clean-build --mesos-version 0.27.2 --os ubuntu:precise
    You are about to remove Mesos build for 0.27.2 ubuntu:precise.
    Are you sure you want to proceed? (y or yes to continue): y
    $> 

### show-mesos-sources

List git origins with Mesos sources.

### show-packaging-sources

List git origins with `mesos-deb-packaging` sources.

## Docker images

The toolbox comes with a bunch of Docker files for the Mesos build process. There is one Docker file per operating system. These files can be found in the `docker` folder.  
It is possible to use an alternative directory containing your own Docker file. To do so, use `--docker-templates` configuration option.  
The assumption is:

    $> DOCKER_TEMPLATES_DIR=/tmp/alternative-docker-templates
    $> ls -la $DOCKER_TEMPLATES_DIR/
    ...
    drwxr-xr-x  3 rad  staff  102 26 Mar 23:37 alpine:3.1
    ...
    $> ls -la $DOCKER_TEMPLATES_DIR/alpine\:3.1/
    total 8
    drwxr-xr-x  3 rad  staff  102 26 Mar 23:37 .
    drwxr-xr-x  7 rad  staff  238 26 Mar 23:36 ..
    -rw-r--r--  1 rad  staff  756 26 Mar 23:37 Dockerfile
    $> 

To build for the system shown above, the following command can be used:

    $> mesos-toolbox.py build --mesos-version master --os alpine:3.1

## The build failed, what do I do

OK, so the build has failed with the error message similar to this:
  
    $> mesos-toolbox.py build --mesos-version 0.27.2 --os fedora:23
    ...
    INFO:mesos-toolbox.py:Recording build process to /Users/rad/.mesos/temp/0.27.2-fedora-23.1459293623.log.
    ...
    ERROR:mesos-toolbox.py:Mesos build failed. Leaving build log and temp directories for inspection. mesos=/Users/rad/.mesos/temp/0.27.2-fedora-23; packaging=/Users/rad/.mesos/temp/0.27.2-fedora-23-packaging

The program has left the following artefacts on the drive:

- `<work-dir>/0.27.2-fedora-23.1459293623.log`
- `<work-dir>/0.27.2-fedora-23`
- `<work-dir>/0.27.2-fedora-23-packaging`

You can find the docker command used for the last build in the log file:

    $> cat <work-dir>/.mesos/temp/0.27.2-fedora-23.1459293623.log | grep 'docker run'
    docker run -ti -v /Users/rad/.mesos/temp/0.27.2-fedora-23-packaging:/mesos-deb-packaging -v /Users/rad/.mesos/temp/0.27.2-fedora-23:/mesos-src mesos-docker-build-fedora-23 /bin/bash -c cd /mesos-deb-packaging

Copy everything until `-c`, paste in your terminal and run. In the container:

    cd /mesos-deb-packaging && ./build_mesos --src-dir /mesos-src

You are set for debugging.

## Configuration

To be added.

## License

Author: Rad Gruchalski (radek@gruchalski.com)

This work will be available under Apache License, Version 2.0.

Copyright 2016 Rad Gruchalski (radek@gruchalski.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License. You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.