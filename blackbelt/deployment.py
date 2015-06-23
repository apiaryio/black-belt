from subprocess import check_call

from blackbelt.handle_github import get_current_branch
from blackbelt.messages import post_message


def deploy_staging():
    branch_name = get_current_branch()

    post_message("Deploying branch %s to staging" % branch_name, "#deploy-queue")

    check_call(['grunt', 'deploy', '--app=apiary-staging', '--force', "--branch=%s" % branch_name])

def deploy_production():
    post_message("Deploying to production", "#deploy-queue")

    check_call(['grunt', 'deploy'])
