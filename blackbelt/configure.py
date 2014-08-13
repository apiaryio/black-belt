from os.path import expanduser
import json
import webbrowser

import handle_trello


def configure_blackbelt():
    print("Going to collect all the tokens and storem them in ~/.blackbelt")
    print('*** Trello ***')
    print("Please get yourself a token: visit %s" % handle_trello.get_token_url())

    webbrowser.open(handle_trello.get_token_url())

    trelloToken = raw_input("Please input the access token: ").strip()

    print('*** GitHub ***')
    tokenUrl = "https://github.com/settings/applications"
    print('Please generate a personal access token at %s' % tokenUrl)
    webbrowser.open(tokenUrl)

    githubToken = raw_input("Please input the access token: ").strip()

    config = {
        'trello': {
            'access_token': trelloToken
        },
        'github': {
            'access_token': githubToken
        }
    }

    with open(expanduser('~/.blackbelt'), 'w') as f:
        f.write(json.dumps(config))

    print('All done!')
