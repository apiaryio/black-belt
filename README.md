# Black Belt

Black belt is collection of scripts, tools and guidelines used for open source project and release management. 

## Installation

`virtualenv` assumed (`sudo easy_install virtualenv`)

```
virtualenv venv
source venv/bin/activate
python setup.py develop
```

## Trello

### Card migration

```
(venv)almad@arael:~/projects/black-belt$ bb t migrate-label --label="Product: Analytics" --board="1KsoiV9e" --board-to="lEL8Ch52" --column-to="Prepared buffer"
Moving card 535e396a8b6363e67962ea5d: Refactor `RedshiftImporter` into separate task
Moving card 5315f2771e7b44597f96ecb4: Properly segregate project data
Moving card 5315f2f4d06fc8277dd58228: Somehow, solve renaming API: analytics shall not be lost when renaming it.
Moving card 5315f36e860dd2380b767da1: Store only a minimal blueprint in Redshift
Moving card 533952a3109b5ad87118767f: Do not call upload repeatedly after timeout
Moving card 5343d9659cd6c062482c9084: Write a test-case for 404 against POST
Moving card 53680d42d430a5e95c6eab09: hain crash
Moving card 538ed78b729aaae73e97e8e6: Geoip decoding before save data into redshift
Moving card 53a0222d37a6a82c1792ab34: Bug in parsing message
Moving card 53a2bf35bdcfc8b3617d8614: Harvester send task on GET request
Moving card 53a2eda59c00e7bbd04622be: Fix failure behaviour for upload when multipart upload init fails
Moving card 53b6d47dfd5d0384ae1736ef: Mock/Proxy server traffic leak
```
