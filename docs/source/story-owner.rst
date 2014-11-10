.. highlight:: c

============
Story Owner
============

:term:`Story Owner` is responsible for a specific user story that's going to be developed. Story lives as a card on a designated Trello Story Board. 

He interacts with :term:`Work Board` as well.

Those are the task :term:`Story Owner` may want to perform. 

------------------------------------
Product list to Work Cards
------------------------------------

:term:`Story Owner` first breaks down the story cards into chunks by putting the list into the :term:`Story`. After this is somehow done and run through with :term:`Developer`, one usually wants to "transer" it to :term:`Work Board` so it can be developed.

.. TODO: bb t schedule-list [--label="Product: Example"] [--work-board="abcdef"] --story-card="defABC" --dev="user-id" [--list="xoxo"]

To help with this task, one can use this command::

	bb t schedule-list [--owner="TrelloUserName" [--story-list="Checklist Name"] [--label="color"] http://trello.com/c/story-card-shortlink

Story list defaults to "To Do", Owner (that the new work tasks are assigned to) defaults to you.

------------
Clean sweep
------------

All cards with the given label is moved from :term:`Work Board` into given column in the :term:`Product Board`. ::

	bb t migrate-label --label="Product: Example" --board="1KsoiV9e" --board-to="lEL8Ch52" --column-to="Prepared buffer"


-------------------------
Get ready for next week
-------------------------

Create new columns on the :term:`Work Board`: `Deployed by <sunday>` and `Verified by <sunday>`

	bb t next-week
