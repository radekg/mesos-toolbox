# Build Mesos locally

Build Mesos for any supported platform locally, with Docker *.
This program is a wrapper for the fantastic [mesos-deb-packaging](https://github.com/mesosphere/mesos-deb-packaging).

## Installation

Clone, make sure you have Docker and Git installed and working. You are ready to go.
This program uses Docker via command line and it works perfectly fine with Docker Toolbox.

    git clone https://github.com/radekg/mesos-toolbox.git
    export PATH=$PATH:`pwd`/mesos-toolbox

## * Supported target operating systems

- `Ubuntu Precise`
- `Ubuntu Trusty`

*More to come soon...*

## Commands

Below is the documentation of all available commands.

### build

    mesos-toolbox.py build --mesos-version 0.27.2 --os ubuntu:precise

## Configuration

To be added.

## How does it work

To be added.

## License

Author: Rad Gruchalski (radek@gruchalski.com)

This work will be available under Apache License, Version 2.0.

Copyright 2016 Rad Gruchalski (radek@gruchalski.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License. You may obtain a copy of the License at

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.