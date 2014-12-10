.. highlight:: bash

============
Developer
============

The :term:`Developer` processes :term:`Work Card`s, develops them and deploys them to production.

Those live on the :term:`Work Board`.

Those are the task :term:`Developer` may want to perform.

.. _development:

------------------------------------
Development as usual
------------------------------------

Open current task
^^^^^^^^^^^^^^^^^

Open current Trello card in browser::

  bb t curcard

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

.. autofunction:: blackbelt.commands.gh.pr
   
------------------------------------
Code review
------------------------------------

Code review ensures the quality of the code and disperses the knowledge about the code and features through the team.


.. _pr-merge:

Merging Pull Request
^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: blackbelt.commands.gh.merge


.. _deploy-pr:

Deploying Pull Requests
^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: blackbelt.commands.gh.deploy
