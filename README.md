# Dockerdd

Dockerdd is a simple Python script to replicate Docker images between
registries.


## Why Dockerdd

If you have multiple registries and want to keep some images in sync, this
script might be your solution. You simply describe the sync in a yaml file and
run the script.


## Installation

To run this script, you will need:

- Python (including pip)
- Docker
- Python's Docker library

To install the Docker library for Python, run the following command:

``` sh
pip install docker
```


## Create the jobs file

This is the structure of a jobs file, it's in yaml format:

``` yaml
registries:
  <registry-name>:
    address: <registry url without the 'http(s)://', or use 'default'>
  <registry-name-2>:
    address: ...

imagelists:
  <imagelist-name>:
    - image1:tag
    - image2:tag
    - image3:tag
  <imagelist-name-2>:
    - ...

jobs:
  <job-name>:
    source: <source registry-name>
    target: <target registry-name>
    imagelists:
      - <imagelist-name-1>
      - <imagelist-name-2>
      - ...
  <job-name-2>:
    source: ...
    ...
```

First define the registries you want to use. Define the registry's address,
e.g. `harbor.mydomain.com/dev-images`. You can also use 'default', in that case
Docker will use the default registry as defined by the Docker configuration.

Next define imagelists. Each imagelist has a name and contains a list of images
(with tags).

Finally defines jobs. Each job copies the given imagelists from the given
source registry to the target registry.

You can define multiple jobs and imagelists. Jobs will be performed in the
given order.


## Run the script

``` sh
dockerdd.py <jobs-file>
```


## Authentication

Some registries require authentication, this is not handled by Dockerdd. You
can authenticate once (manually) using `docker login`, the secrets will be
stored in `~/.docker/config.json`.


## Gitlab pipeline

The file `example-gitlab-ci.yml` demonstrates you how you can run this script
in a pipeline.


## License: GPL 3.0

Copyright (C) Ernest Neijenhuis PA3HCM

Dockerdd is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

Dockerdd is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
Dockerdd. If not, see http://www.gnu.org/licenses/.


## Project information

Author: Ernest Neijenhuis
Code on Github: https://github.com/pa3hcm/dockerdd
