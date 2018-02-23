Wikipedia spider
****************

The goal
--------

Build a CLI tool to eventually get from one `Wikipedia <https://en.wikipedia.org/wiki/Main_Page>`__ article to another,
not linked in the same article, by "crawling" the Wikipedia links within articles.

The setup
---------

The setup is exactly the same as in :ref:`first-setup` in the first task, so you can just create another file in your
current project, and remember to create a *Run Configuration* for it as well to make for easier debugging!

The pieces
----------

Since we want to create a CLI application, I once again recommend to use the :code:`argparse` module. You can get the
boilerplate for it from the ":ref:`second-setup`" section of the task for the top subreddit post CLI tool, but you don't
have to, of course!

This is probably less about BeautifulSoup and requests, but more about application logic. Which is great, since
you'll get to learn how to work with lists, conditionals, loops and such. And working with those in python is lots of
fun!

To get you kickstarted, to get links from a Wikipedia article, you need to look for the :code:`#content` container. But
remember, you don't need external links, just the Wikipedia article ones. The easiest way is to look if their "href"
attribute starts with :code:`/wiki/`! And, thankfully, you can pass a compiled regex pattern to BeautifulSoup's parser!

The code looks something like this:

.. code-block:: python

    import bs4
    import re
    import requests

    response = requests.get('https://en.wikipedia.org/wiki/Python_(programming_language)');
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    # With "r" prefixing the string (defining it as a raw string), we don't need to escape,
    # for instance, backslashes for the regex pattern.
    link_tags = soup.find(id='content').find_all(href=re.compile(r'^/wiki/'))

Also, you need to think of a way create a queue of URLs to visit, and so you don't go to the same place twice - check
if the link you're about to visit hasn't already been visited. Or, perhaps, you eliminate duplicates in your queue, it's
up to you.

Good luck in the task! And feel free to ask me or check the solution if you need any help!

Oh, one more thing - in comparison to Reddit, Wikipedia doesn't mind bots and won't throttle your requests, so no
UA string spoofing needed!

In conclusion
-------------

While `Degrees Of Wikipedia <http://www.degreesofwikipedia.com/>`__ does the job better and faster than we can do now,
they also probably spent way more time on their tool. But just knowing how to write a web crawler can one day prove
to be a quite useful and handy skill. Remember, this is pretty much the stepping stone to writing the next big search
engine!

Solution
--------

Again, here's a :download:`solution <third.py>` if you feel stuck and need some sort of a hint. Obnoxious amounts
of comments included!

With my method it took:

* 13 requests to get from `Justin Bieber <https://en.wikipedia.org/wiki/Justin_Bieber>`__ to
  `Slayer <https://en.wikipedia.org/wiki/Slayer>`__
* 41 request to get from `Batman <https://en.wikipedia.org/wiki/Batman>`__
  to `Morgan Freeman <https://en.wikipedia.org/wiki/Morgan_Freeman>`__
* a whopping 2392 requests to get from `Blockchain <https://en.wikipedia.org/wiki/Blockchain>`__ to
  `Potato <https://en.wikipedia.org/wiki/Potato>`__! Here's a `log of the whole trip <https://gist.github.com/pundurs/27f46ea9203fa4dd8f7897c692ecf5e3>`__.
