# Import a bunch of stuff we're going to need
import argparse
import bs4
import datetime
import math
import re
import requests
import sys
from collections import namedtuple


# the named tuple is a great container to store data in, if you don't want a class,
# want an immutable data type, like the tuple, but want to access it through attributes
# instead of indexes.
CrawlResult = namedtuple('CrawlResult', ['hops', 'timedelta', 'success', 'last'])


class WikiSpiderException(Exception):
    """
    Exception raised by the WikiSpider class.
    All exception subclasses should inherit from Exception.
    """


class WikiSpider(object):
    """
    Our spider class.
    All classes should inherit from "object"
    """
    # We define a bunch of class attributes
    # They're sorta like static fields,
    # but you can still change them per instance
    host = 'https://en.wikipedia.org'
    suffix = '/wiki/'
    url = host + suffix

    # We're going to use a simple regular expression
    # to filter our inner Wiki links
    wiki_link_pattern = re.compile(r'^' + suffix)

    def __init__(self, start, target):
        """
        The initializer - requires two arguments.
        :param start: Starting wikipedia page slug
        :param target: Target wikipedia page slug
        """
        # We assign the arguments to our instance
        self.start = start
        self.target = target

        # Since python doesn't have keywords like "private"
        # or "protected", we prefix our variables with an
        # underscore to let developers using our API know
        # that these are not part of the public API.
        # Keep in mind, this is not, standard, but just a
        # generally accepted convention, which also an IDE
        # like PyCharm understands.
        self._hops = 1

        # Store the initialization time, so we can measure
        # the duration of our trip.
        self._now = datetime.datetime.now()

        # Here we'll store the links we'll visited and the
        # links we still have to visit.
        self._visited = []
        self._queue = []
        self._start_response = None

    def _check_urls(self):
        """
        This function only takes one argument - the instance itself,
        which makes it a method, callable with self._check_urls()

        Just like with "private" variables, we're using an underscore prefix
        to indicate a private method.

        :return: None
        """
        # Store the first response, so we don't need to repeat this request again
        start_url = self._get_full_url(self.start)
        self._start_response = requests.get(start_url)

        # This way we know if the provided arguments for "start" and "target"
        # are valid Wikipedia pages.
        if self._start_response.status_code == 404:
            raise WikiSpiderException('The provided start Wikipedia page doesn\'t exist.')

        # Mark the start page as visited.
        self._visited.append(self.suffix + self.start)

        # Check the target page as well, of course, so we know our eventual destination exists.
        target = requests.get(self.url + self.target)
        if target.status_code == 404:
            raise WikiSpiderException('The provided target Wikipedia page doesn\'t exist.')

    def crawl(self):
        """
        This is a public method, since we're not prefixing.
        :return:
        """
        # Check if the pages are valid
        self._check_urls()

        # Check if the start response doesn't contain our target page
        links = self._get_links(self._start_response)
        if self._check(links):
            # And it does, we can return a successful result right away!
            return self._result(True, 'the starting page!')

        # Start creating a queue of links to visit
        self._add_to_queue(links)

        while True:
            # Here we start an endless loop which we will
            # break manually if we get to our destination.
            try:
                # the pop() method returns and removes the item at the same time.
                # without an index argument it returns the last element, but since
                # we have a queue and not a stack - we take the first one.
                # But we have to prepare for a potential IndexError, and one of the times
                # it's raised is when you call pop() on an empty list.
                next_url = self._queue.pop(0)
            except IndexError:
                # With wikipedia this shouldn't be possible, but we somehow ran out
                # of URLs to check, so we return a negative result
                return self._result(False)

            # This could have been added to the regular expression, but it was late
            # and I got lazy.
            # Basically, we just check if the crawled URL isn't an internal Wikipedia page.
            if '/wiki/Wikipedia' in next_url or '/wiki/Special' in next_url:
                # The continue statement tells python that it should jump to the
                # next iteration of the loop right away.
                continue

            if next_url in self._visited:
                # Of course, we don't want to visit pages we've already been in.
                continue

            # Print some progress output.
            print('Hopping (%d). Next url' % self._hops, next_url)

            # Append the page we're about to visit to the visited ones.
            self._visited.append(next_url)

            # Use our method to get the links from an article and increase the hop count by 1
            links = self._get_links_from_wiki_link(next_url)
            self._hops += 1

            if self._check(links):
                # It seems we got to our destination page. Return a positive result
                return self._result(True, last_page=self.host + next_url)

            # Add the collected links from the page to the queue.
            self._add_to_queue(links)

    def _add_to_queue(self, urls):
        """
        A private method we use to add links we've gotten from an article to the queue
        :param urls:
        :return:
        """
        for url in urls:
            if url in self._queue or url in self._visited:
                # If the URL we're iterating on has already been visited, we, of course,
                # don't add it to the queue.
                continue

            # The URL doesn't seem seen before, so we add it to the queue list.
            self._queue.append(url)

    def _check(self, urls):
        """
        We use this method to check if any of the wikipedia links we've gotten from
        an article don't match the URL to the page we're trying to get to.

        any(), basically takes an iterable and if any of the elements in it has a
        "truthy" value, any() will return True. Otherwise False.

        With the "<comparison> for <item> in <iterable>" we generate an iterable
        of booleans. You can see it as a sort-of syntactic sugar for map()
        """
        return any(self.suffix + self.target == url for url in urls)

    def _get_full_url(self, page_slug):
        """
        A small convenience method to glue 'https://en.wikipedia.org/wiki/' with an article slug.
        """
        return self.url + page_slug

    def _get_links_from_wiki_link(self, url):
        """
        A shortcut method to get links from a "/wiki/Some_Article" URL.
        """
        return self._get_links(requests.get(self.host + url))

    def _get_links(self, response):
        """
        A method to get a list of URLs from a requests.Response object.
        """
        if response.status_code != 200:
            # If somehow we've gotten anything other than a successful
            # response, we return an empty list.
            return []

        # We initialize the beautifulsoup parser with our response content.
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        # Using BS, we first find the element '#mw-content-text', which is
        # the main article container - in it, we're looking for all elements
        # which have a "href" attribute, which starts with "/wiki/" by using
        # a regular expression.
        links = soup.find(id='mw-content-text').find_all(href=self.wiki_link_pattern)

        # Again, using the syntactic sugar for map, to only get the href attributes
        # from bs4.Tag instances as a list.
        return [result['href'] for result in links]

    def _result(self, result, last_page=''):
        """
        A small convenience method to return our CrawlResult named tuple
        We have an optional keyword argument "last_page" with a default value
        of an empty string.
        """
        return CrawlResult(self._hops, self.get_elapsed_time(), result, last_page)

    def get_elapsed_time(self):
        """
        This is a public method to get a datetime.timedelta object, which contains
        the time passed, since our WikiSpider instance was initialized.
        :return: datetime.timedelta
        """
        return datetime.datetime.now() - self._now


def main(start, target):
    """
    This is the main (which doesn't even need to be called main())
    function which we will wrap in an exception handler to
    catch a KeyboardInterrupt event, so we can exit cleanly.
    :param start: Starting Wikipedia page
    :return:
    """
    # We instantiate our WikiSpider class.
    spider = WikiSpider(start, target)

    # and our main() function returns the result of calling the crawl() method
    # of the WikiSpider instance. This might take a while ...
    return spider.crawl()


if __name__ == '__main__':
    """
    This part of the code runs only if the script is invoked directly
    instead of being imported from a different module.
    """

    # Create an ArgumentParer with a description of what our script does.
    parser = argparse.ArgumentParser(
        description='Count how long and how many hops it takes to get to a target '
                    'Wikipedia page. You can get the '
    )

    # We add our positional arguments.
    # For the add_argument() method, the first argument is the attribute we can access
    # after parsing our arguments, then we add a help text and define the type.
    parser.add_argument('start', help='Slug of page from which to start', type=str)
    parser.add_argument('target', help='Slug of target page', type=str)

    # We parse the user's input and check if all the required arguments were supplied
    args = parser.parse_args()

    try:
        # We're trying to call the main() function with the user's provided arguments
        #  here and hope that we don't raise an exception.
        print('Running. Press Ctrl+C to exit.')
        result = main(args.start, args.target)
    except WikiSpiderException as e:
        # The WikiSpider class raised an exception,
        # probably because of a non-existing start
        # or target page.
        # We just print the exception message to the user.
        print(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        # The user got tired of waiting and pressed Ctrl+C,
        # so we exit cleanly.
        print('Exiting.')
        sys.exit(0)

    print('All done!')

    # We get the amount of total seconds passed by calling the
    # total_seconds() method of the deltatime instance
    total_seconds = result.timedelta.total_seconds()

    # And do simple arithmetic to get the whole minutes passed
    # as an integer.
    minutes = int(math.floor(total_seconds / 60))

    try:
        # Now, we get the remainder of the seconds passed
        # with modulo (remainder)
        seconds = total_seconds % int(60 * minutes)
    except ZeroDivisionError:
        # zero minutes passed, so we handle the zero-division error
        seconds = int(total_seconds)

    # We can return different values based of a boolean result with
    # value_if_true if something_is_true else value_if_false
    print('Result:', 'success!' if result.success else 'failure.')
    if result.success:
        print('Target page linked at %s' % result.last)
    print('Time elapsed %sm %ss.' % (minutes, seconds))

    # Here we print a singular form "hop" if the number of hops converted to a string ends with a 1.
    print('Did %s %s.' % (result.hops, 'hop' if str(result.hops)[-1:] == '1' else 'hops'))
