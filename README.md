# Black Belt

Black belt is collection of scripts, tools and guidelines used for developing projects The Apiary Way.


## Installation & Usage

Please refer to [The Black Belt Documentation](http://black-belt.readthedocs.org/).


## If you want to develop black-belt...

`virtualenv` assumed (`sudo pip install virtualenv`) and Python 2.7

```
virtualenv venv
source venv/bin/activate
pip install paver
pip install -r requirements-development.txt
paver develop
paver test
```

### Testing

`paver test`

If you ran `bb init` and you want to do "discovery testing" with the integration tests,
set `FORCE_DISCOVERY`environment variable to `1`.

### Release

When the time is right, run `paver bump`.

When adding new feature (command etc), run `paver bump major` instead.

After it, just call `paver release` and enjoy your PyPI.

Note: GPG must be properly configured for usage with `git tag -s` and you must be project maintainer on PyPI.

