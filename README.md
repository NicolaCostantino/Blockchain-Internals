[![Build Status](https://travis-ci.com/NicolaCostantino/Blockchain-Internals.svg?branch=master)](https://travis-ci.com/NicolaCostantino/Blockchain-Internals)
[![codecov](https://codecov.io/gh/NicolaCostantino/Blockchain-Internals/branch/master/graph/badge.svg)](https://codecov.io/gh/NicolaCostantino/Blockchain-Internals)


# Blockchain-Internals
Proofs of Concept and sample implementations of a Blockchain in Python.

## Table of Contents

* **[Setup](#setup)**
  * [Python](#python)
  * [Requirements](#requirements)
* **[Usage](#usage)**
  * [Example](#usage-example)
* **[Development](#development)**
  * [Code](#development-code)
  * [Setup](#development-setup)
  * [Testing](#development-testing)
* **[Contributing](#contributing)**
* **[Author](#author)**
* **[License](#license)**
* **[Acknowledgments](#acknowledgments)**
  * [Inspiration](#inspiration)

## Setup <a name="setup"></a>

### Python <a name="python"></a>
Required version: 3.7.*  

Use [pyenv](https://github.com/pyenv/pyenv) or [pyenv-installer](https://github.com/pyenv/pyenv-installer) to easily switch between multiple versions of Python.  
[Pipenv](https://github.com/pypa/pipenv) will automatically suggest and install the right version for this project.

### Requirements <a name="requirements"></a>
Use [Pipenv](https://github.com/pypa/pipenv) to install the requirements needed
```bash
pipenv install
```
If [pyenv](https://github.com/pyenv/pyenv) is installed, [Pipenv](https://github.com/pypa/pipenv) will automatically suggest and install the right version for this project. 

## Usage <a name="usage"></a>
All the needed commands are listed as [GNU `make`](https://www.gnu.org/software/make/) target rules in the [Makefile](Makefile) file.  
Each subfolder could contain a local Makefile file, if needed.  
Run the target rule with:  
```bash
make <target_rule>
```
### Example <a name="usage-example"></a>
Example: Run Jupyter Labs
```bash
make jupyter_lab
```

## Development <a name="development"></a>

### Code <a name="development-code"></a>
The source code is hosted on [GitHub](https://github.com/NicolaCostantino/Blockchain-Internals).

### Setup <a name="development-setup"></a>
Use [PipEnv](https://github.com/pypa/pipenv) to install also the requirements for development and testing
```bash
pipenv install --dev
```

### Testing <a name="development-testing"></a>
Tests are executed using [PyTest](https://docs.pytest.org/en/latest/) and [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) plugin for coverage.

## Contributing <a name="contributing"></a>
Pull requests are welcome!  

For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Author <a name="author"></a>
[Nicola Costantino](https://github.com/NicolaCostantino)  

## License <a name="license"></a>
[MIT](https://choosealicense.com/licenses/mit/) as listed in [LICENSE file](LICENSE)  
Copyright (c) 2019 Nicola Costantino

## Acknowledgments <a name="acknowledgments"></a>
### Inspiration <a name="inspiration"></a>
* ["Let's Build a Blockchain"](https://github.com/Haseeb-Qureshi/lets-build-a-blockchain), by Haseeb Qureshi
* ["Learn Blockchains by Building One"](https://github.com/Haseeb-Qureshi/lets-build-a-blockchain), by Daniel van Flymen