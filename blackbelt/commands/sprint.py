import click, re
from blackbelt.config import config

from blackbelt.handle_trello import get_api, verify

@click.group(help='Team trello actions for sprints')
def cli():
    pass

@cli.command(name='bp')
def blueprint_plan():
    """ Starting sprint planning for Team Blueprint™ """
    api = get_api()

    print "Retrieving the relevant columns ..."

    product_columns = api.get_columns(config['trello']['product_board_id'])

    current_sprint_column = None
    next_sprint_column = None

    print "Retrieving the stories in the current sprint ..."

    for column in product_columns:
        if re.match("^Sprint\\ (.*)\\ \\([0-9]+\\)$", column['name']):
            current_sprint_column = column

        if column['name'] == 'Next Sprint':
            next_sprint_column = column

    if current_sprint_column is None:
        raise ValueError("Unable to find current sprint list in product board")

    if next_sprint_column is None:
        raise ValueError("Unable to find the next sprint list in prodcut board")

    stories = api.get_cards(current_sprint_column['id'])

    for story in stories:
        print "Checking the status of '" + story['name'] + "' ..."

        if not verify(story, 'Merged by', 'Released by', False):
            api.move_card(story['id'], None, next_sprint_column['id'])

    print "Done"

@cli.command(name='bs')
def blueprint_schedule():
    """ Starting sprint for Team Blueprint™ """
    pass
