
======================================
Project automation the Apiary way
======================================

This is an internal tool for supporting development workflow inside `Apiary <http://apiary.io/>`_. However, we decided to open-source it. Feel free to fork it and use it on your own or inside your company.


--------------
Installation
--------------

``pip install blackbelt`` if you can, ``easy_install blackbelt`` if you must (Mac OS X default).

With that, you should have ``bb`` command. Run interactive ``bb init`` and follow instructions. This is going to connect to services we are using in Apiary for futher interaction:

* GitHub
* Trello

Retrieved tokens and configuration is stored in ``~/.blackbelt``. Format is now just dumped JSON, don't rely on it; it's probably going to change in the future.

If you are using ``bash``, you want to enable autocompletion. You can try it with::

	eval "$( _BB_COMPLETE=source bb)"

and if it's working properly, put it into your :file:`~/.bashrc`::

	echo '_BB_COMPLETE=source bb > /tmp/_black_belt_autocompletion.sh'  >> ~/.bashrc
	echo 'source /tmp/_black_belt_autocompletion.sh' >> ~/.bashrc


See `click's documentation <http://click.pocoo.org/3/bashcomplete/>`_ for more information.

If you are using ``zsh``, you want to enable autocompletion.

You can try it plugin for [Oh-my-zsh](https://github.com/robbyrussell/oh-my-zsh) and enable it in :file:`~/.zshrc`::

  plugins=(bb)

--------------
Structure
--------------

`bb` has subcommands that stand for an area of expertise. View help or command reference on how to use those.

This documents focus more on intended workflow from the perspective of two roles (those may be the same person, of course): Developer and Story Owner.


.. toctree::
   :maxdepth: 2

   developer
   story-owner
   glossary



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

