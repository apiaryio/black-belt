from os.path import expanduser, exists
import json
import webbrowser

import click

import handle_trello

CONFIG_FILE = expanduser('~/.blackbelt')


def get_token(config, token_url, group_name, address_text="Please generate a token for yourself:"):
    print '*' * 3 + ' ' + group_name + ' ' + '*' * 3
    print address_text + ' ' + token_url

    default_token = None
    if group_name in config and config[group_name]['access_token']:
        default_token = str(config[group_name]['access_token'])

    webbrowser.open(token_url)

    token = click.prompt("Please insert an access token", default_token)

    if group_name not in config:
        config[group_name] = {}

    config[group_name]['access_token'] = token


def configure_blackbelt():
    print("Going to collect all the tokens and store them in ~/.blackbelt")

    config = {
        'trello': {
            'access_token': None
        },
        'github': {
            'access_token': None
        },
        'circleci' : {
            'access_token' : None
        },
        'hipchat': {
            'access_token': None
        }
    }

    if exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            config = json.loads(f.read())

    get_token(
        group_name='trello',
        config=config,
        token_url=handle_trello.get_token_url()
    )

    get_token(
        group_name='github',
        config=config,
        token_url="https://github.com/settings/applications"
    )

    get_token(
        group_name='circleci',
        config=config,
        token_url="https://circleci.com/account/api"
    )

    get_token(
        group_name='hipchat',
        config=config,
        token_url="https://apiary.hipchat.com/account/api"
    )


    with open(expanduser('~/.blackbelt'), 'w') as f:
        f.write(json.dumps(config))

    print('All done!')
