# Black Belt

Black belt is collection of scripts, tools and guidelines used for developing projects The Apiary Way.


## Installation & Usage

Please refer to [The Black Belt Documentation](http://black-belt.readthedocs.org/).

```
$ brew install pipenv
```
or

```
$ sudo apt install software-properties-common python-software-properties
$ sudo add-apt-repository ppa:pypa/ppa
$ sudo apt update
$ sudo apt install pipenv
```

Otherwise, just use pip:

```
$ pip install pipenv
```


## If you want to develop black-belt...

Install all dependencies for a project (including dev):

```
pipenv install --dev
paver test
```

### Testing

`paver test`

If you ran `bb init` and you want to do "discovery testing" with the integration tests,
set `FORCE_DISCOVERY`environment variable to `1`.

### Troubleshooting

If you try run `paver bump` and get error `TypeError: 'map' object is not subscriptable` you can run `./venv/bin/paver bump` to fix this.

### Release

When the time is right, run `paver bump`.

When adding new feature (command etc), run `paver bump major` instead.

After it, just call `paver release` and enjoy your PyPI.

Note: GPG must be properly configured for usage with `git tag -s` and you must be project maintainer on PyPI.

