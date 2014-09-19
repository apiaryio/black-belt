.. highlight:: bash

============
Developer
============

:term:`Developer` processes :term:`Work Card`s, develops them and deploys them to production.

Those live on the :term:`Work Board`.

Those are the task :term:`Developer` may want to perform. 

.. _development:

------------------------------------
Development as usual
------------------------------------

.. _next-card:

Move on to the next task
^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^

Send current branch for code review with::

	bb gh pr

This:

#. Inspects current repository for branches
#. Inspects ``Doing`` on the :term:`Work Board` for the current working ticket (you should have only one working ticket in ``Doing`` that is assigned only to you)
#. Creates a pull request that references the trello card and references the PR on the card as well
#. Moves the card to ``Ready``
#. Opens the browser with the PR for further editing/review

------------------------------------
Code review
------------------------------------

Code review ensures the quality of the code and disperses the knowledge about the code and features through the team.


.. _pr-merge:

Merging Pull Request
^^^^^^^^^^^^^^^^^^^^^

Merge PR on Github into master with::

	bb gh merge https://github.com/apiaryio/apiary/pull/1234

This:

#. Inspects the current repository and the pull request
#. Switches to master and brings it up to date
#. Merges the PR locally and pushes to master
#. Deletes the merged branch from the remote repository/github

TODO:

* Comment the associated Trello card


.. _deploy-pr:

Deploying Pull Requests
^^^^^^^^^^^^^^^^^^^^^^^^

Deploy PR to production with::

	bb gh deploy https://github.com/apiaryio/apiary/pull/1234

This:

#. Does :ref:`pr-merge`
#. Inform people on HipChat about the merge and the deployment intent
#. Prepares Heroku deploy slugs using ``grunt create-slug``
#. Waits for CircleCI tests to pass
#. TODO: If they fail, asks for retry
#. Asks for deploy confirmation
#. Notify others on HipChat about deploy
#. Deploys
#. If it can figure out related Trello card (looks for "Pull request for <link>"), moves it to "Deployed by" column
#. Does *not* bring beer yet, unfortunately
