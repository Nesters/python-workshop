Bulk image downloading
**********************

The goal
--------

Download the *Most Viral images on the Internet ©* from `imgur <https://imgur.com/>`_.

.. _first-setup:

The setup
---------

You will need to install the :code:`requests` and :code:`beautifulsoup4` packages. There are multiple ways to do it, but
the fastest one is opening up a a terminal in PyCharm (*Alt+F12*) - your *virtualenv* will already be activated as indicated
by :code:`(venv)` prefixing your prompt. Type in the following commands:


.. code-block:: bash

   pip install requests
   pip install beautifulsoup4

The pieces
----------

Here are the main pieces of the puzzle. Since we're limited on time, I'll tell you the steps so you don't have to do the
"detective" work yourself.

If you open imgur.com in your browser's inspector and pick any of the thumbnails, you might notice that they have a
common thing - they are wrapped in :code:`a` elements with the class :code:`image-list-link`.

Inside of that link resides an :code:`img` element with a :code:`src` attribute pointing to a file. If you open the file,
you'll see that it's a thumbnail.

So how do we get to the large image? If you look closer at the thumbnail URLs, you'll notice that all of them are ending
with *b* before the extension. What happens when we remove that *b*? Voilà, we get the enlarged image (or, a frame if it's
a video, but determining if it's a gif, image or video is, unfortunately, out of scope for this workshop)

So, in short - you need to get all the :code:`src` `attributes <https://www.crummy.com/software/BeautifulSoup/bs4/doc/#attributes>`__
from the images, modify them not to contain the trailing *b* before the `extension <https://docs.python.org/3/library/os.path.html#os.path.splitext>`__, and use that to get the large images,
which you need to `save somewhere <https://docs.python.org/3/library/functions.html#open>`__!

Feel free to ask me if anything is unclear to you! Here are your first 2 lines. Good luck!

.. code-block:: python

    import bs4
    import requests

In conclusion
-------------

While the script might is far from perfect - a lot of images, if not even most on *imgur* now are gifs or videos, you
are already on the way to getting a nice dose of internet humor straight to your hard drive!

Are you ready to take a crack at creating a :doc:`second`?

Solution
--------

If you feel like taking a peek - you can check :download:`my solution <first.py>` with way too many comments, to help
you understand what the code does.