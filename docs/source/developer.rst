.. highlight:: bash

=========
Developer
=========

The :term:`Developer` processes :term:`Work Cards`, develops them and deploys them to production.

Those live on the :term:`Work Board`.

Those are the task :term:`Developer` may want to perform.

.. _development:

--------------------
Development as usual
--------------------

Open current task
^^^^^^^^^^^^^^^^^

Open current Trello card in browser::

  bb t curcard

.. _next-card:

Move on to the next task
^^^^^^^^^^^^^^^^^^^^^^^^

Move on to the next (Trello) card with::

	bb t next

This:

#. Inspects ``To Do`` on the :term:`Work Board` for the highest ticket assigned to you
#. Creates a new local git branch inferred from ticket name and prefixed with your github prefix
	(It is always forked from master and ensures master is up to date)
#. Moves the card to ``Doing``
#. Opens the card in browser for review


.. _issue-pr:

Issuing Pull Request
^^^^^^^^^^^^^^^^^^^^

.. autofunction:: blackbelt.commands.gh.pr_command

.. autofunction:: blackbelt.dependencies.pull_request

Checking Dependencies
^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: blackbelt.commands.dep.check

.. autofunction:: blackbelt.handle_github.check

-----------
Code review
-----------

Code review ensures the quality of the code and disperses the knowledge about the code and features through the team.

.. _check-status:

.. autofunction:: blackbelt.commands.gh.status_command

.. autofunction:: blackbelt.handle_github.check_status


.. _pr-merge:

Merging Pull Request
^^^^^^^^^^^^^^^^^^^^

.. autofunction:: blackbelt.commands.gh.merge_command

.. autofunction:: blackbelt.handle_github.merge


.. _deploy-pr:

Deploying Pull Requests
^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: blackbelt.commands.gh.deploy_command

.. autofunction:: blackbelt.handle_github.deploy


Deploying master
^^^^^^^^^^^^^^^^

.. _deploy-production:

Deploy current branch to production with::

  bb production

This:

#. Informs others on Slack
#. Deploys master to production using ``grunt deploy``


-------
Testing
-------

.. _deploy-staging:

Deploy current branch to staging with::

	bb stage

This:

#. Discovers what the current branch is
#. Informs others on Slack
#. Deploys the branch to staging using ``grunt deploy``

