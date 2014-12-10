import re

from blackbelt.apis.papertrail import Papertrail


def trello_url_error(search_url):
    match = re.match(r"^https://papertrailapp.com/searches/(?P<id>\d+)", search_url)
    if not match:
        raise ValueError("Cannot find search id")

    id = match.groupdict()['id']

    print "Reverse-search for ID %s will be implemented once supported by Papertrail API"
