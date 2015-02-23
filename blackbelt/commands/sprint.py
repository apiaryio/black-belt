import click, re, datetime
from blackbelt.config import config

from blackbelt.handle_trello import get_api, verify, next_week

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
def blueprint_start():
    """ Starting sprint for Team Blueprint™ """
    api = get_api()
    points = 0

    ##########################################

    print "Preparing ..."

    work_columns = api.get_columns(config['trello']['work_board_id'])
    product_columns = api.get_columns(config['trello']['product_board_id'])

    ##########################################

    print "Archiving relevant columns ..."

    for column in work_columns:
        if re.match("^(Merged|Released)\\ by\\ ", column['name']):
            api.close_column(column['id'])

    ##########################################

    print "Creating new columns ..."

    monday = datetime.date.today()

    while monday.weekday() != 0:
        monday += datetime.timedelta(1)

    friday = monday + datetime.timedelta(11)

    next_week(friday, 'Merged by', 'Released by')

    ##########################################

    print "Retrieving the stories for next sprint ..."

    next_sprint_column = None

    for column in product_columns:
        if column['name'] == 'Next Sprint':
            next_sprint_column = column
            break

    stories = api.get_cards(next_sprint_column['id'])

    for story in stories:
        print "Scheduling tasks for '" + story['name'] + "' ..."

        match = re.match("^(.*)\\ \\(([0-9]+)\\)$", story['name'])

        if match:
            points += int(match.group(2))

    ##########################################

    print "Magicking the labels ..."

    ##########################################

    print "Renaming columns ..."

    api.rename_column(next_sprint_column['id'], "Sprint %s - %s (%d)" % (monday, friday, points))

    ##########################################

    print "Finishing ..."

    api.add_column(config['trello']['product_board_id'], "Next Sprint", 6)

    print "Done"
