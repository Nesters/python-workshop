
# Alphabetically sorted imports are my guilty-pleasure!
import argparse
import bs4
import csv
import requests
import sys


class RedditScraperException(Exception):
   """
   Exception thrown by RedditScraper.
   All exceptions should inherit from "Exception"

   Notice how a docstring is enough to just declare
   a class which inherits from another one?
   """


class RedditScraperResponseException(RedditScraperException):
    """
    We wil throw this exception if the subreddit
    doesn't exist

    We inherit it from our base exception.

    Also, unlike, for example, Java, there is no convention
    that a Python module can't have more than 1 class declaration,
    but in time, if the code base increases, we would separate our
    code in multiple packages and modules.

    For the sake of example, i wrote a pass statement in the declaration.
    You can use that if you want to indicate that "nothing happens"
    in that particular location. Works in if statements, loops, method,
    class declarations, literally everywhere and very useful if you're
    working on code isn't implemented yet.
    """
    pass


class RedditScraperWriteException(RedditScraperException):
    """

    """


class RedditScraper(object):
    """
    Gets the top 10 posts from a subreddit
    and saves them in a CSV file
    """
    def __init__(self, subreddit_name):
        """
        This is Python's version of a constructor, although,
        technically the object is constructed before this code runs,
        so this method is called an "initializer".

        If our class would inherit from another class, we would
        also add a call to super().__init__() here to call the initializer
        of the parent class(-es).

        The following two lines are in case we would generate a reference doc
        for our "library", which Sphinx is able to parse, but they are optional,
        of course:
        :param subreddit_name: Subreddit to get the top posts from
        :type subreddit_name: str
        """
        self.subreddit = subreddit_name

        # We perform the request right in the initializer,
        # since, if the subreddit doesn't exist, there's no point
        # in continuing
        #
        # Also, the response object isn't meant to be in the public API
        # of our class, but since there is no "private" keyword like in
        # other languages, we just, by convention, prefix it with an underscore
        # to let people which utilize our library know, that this is only
        # meant for internal use.
        #
        # Since reddit throttles bot requests, we spoof the User Agent.
        self._response = requests.get(self.build_url(), headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'
        })

        # Since reddit doesn't return a 404 on a non-existing subreddit,
        # but redirects to a search page, we check for a string.
        if 'there doesn\'t seem to be anything here' in self._response.text:
            # Empty search page, so we let the caller know by raising an exception
            # since there's no point to continue.
            raise RedditScraperResponseException(f'The subreddit "{subreddit_name}" doesn\'t seem to exist.')

        # If we've gotten this far, it looks like we got a legit subreddit!

    def build_url(self):
        """
        Get the URL for the top posts for the subreddit.

        This is a method, with the first argument "self"
        which refers to the instance.
        :return: str
        """
        # Format strings are pretty sweet, but they are just one
        # of many ways you can build a string.

        # You can put pretty much any type of python expression
        # between the square brackets!
        # (notice the "f" prefixing the string)
        return f'https://www.reddit.com/r/{self.subreddit}/top'

    def write(self, output):
        """
        Write the 10 most popular posts to a CSV file

        This method uses has one argument - output.

        The return type "None" indicates that this is a "void" method
        i.e. it doesn't return anything

        :param output: Path to output CSV file
        :type output: str
        :return: None
        """

        # Business as usual - initialize BeautifulSoup with our HTML and the default parser.
        soup = bs4.BeautifulSoup(self._response.text, 'html.parser')

        # Get the first 10 posts within the reponse
        entries = soup.find_all(class_='thing')[:10]

        # Well, we're dealing with writing to a user supplied location
        # so something will definitely crash and burn at some point.
        try:
            # Unlike the previous task, since we want to write CSV,
            # we open the file in writable text mode, and not binary mode
            # and, since text mode is the default for open(), we just ommit
            # the "b" in the mode argument.
            # Also, we tell it that we don't have a newline character, since
            # the csv writer will create them for us. Otherwise we will have
            # useless blank lines in our final CSV.
            with open(output, 'w', newline='') as f:
                # We define our field names (so the writer knows the order when writing the rows) and create a
                # DictWriter object, which will write a nicely formatted CSV file by consuming dictionaries.
                # Of course a regular writer() can be used which takes lists as it's argument to writerow().
                field_names = ['upvotes', 'title', 'link']
                writer = csv.DictWriter(f, fieldnames=field_names)

                # Write the first row
                writer.writeheader()

                # We iterate over the posts
                for post in self._get_entry_iter(entries):
                    # And write the row, by supplying the only argument
                    # Conveniently, writerow() accepts both
                    writer.writerow(post)

        # the OSError is a nice common denominator for these kinds of errors
        # this time we store the exception instance in a reference "e".
        except OSError as e:
            # We throw our own exception instead since it inherits from our base
            # exception and makes error handling for the library consumer easier
            #
            # We do throw it with the original exception message though which we
            # can get by casting the exception instance to a string
            # (to define this behavior for your own classes, override the __str__()
            # dunder method)
            raise RedditScraperWriteException(str(e))

    # We decorate this method as a static method.
    # That tells the interpreter that the first argument won't be
    # the instance itself.
    @staticmethod
    def _get_entry_iter(entries):
        """
        This method will go over all the entries supplied
        and yield a dictionary of post metadata like upvote count,
        the title, author and the link to the post.

        A method/function that "yields" instead of "returns" is called a generator.
        Generators can't be accessed by index (by using the bracket notation
        like [0]), they can only be iterated on, i.e. used in loops,
        iterable operations like map/reduce/filter etc.

        Using generators is more memory efficient, since only the current entry
        which is being iterated on is kept in memory instead of all of them, like
        in the case of a list.

        While for a 10 item list a generator might be overkill, it's good to
        know how to write a generator in case you need to work with a large number of
        entries or a lot of entries.
        :param entries: An iterable of reddit posts.
        :type entries: bs4.element.Tag
        """
        for e in entries:
            # Since there are 3 elements for upvoting, we need to take the second element
            upvotes = e.find_all(class_='score')[1].text

            # Conveniently, the title text is the first link within the post container
            # and it links to the article
            title = e.find('a')
            title_text = title.text
            link = title['href']

            # And we yield a dictionary.
            # The keys have to coincide with the field names we defined for the writer.
            yield {
                'upvotes': upvotes,
                'title': title_text,
                'link': link
            }


def handle_exception(e):
    """
    We define a common way to handle exceptions thrown within the CLI script.
    :param e: An exception thrown by RedditScraper
    :type e: RedditScraperException
    :return:
    """
    # Write the exception message to STDERR and exit with a code of 1
    # to indicate that our script didn't complete successfully
    sys.stderr.write(str(e))
    sys.exit(1)


if __name__ == '__main__':
    """
    This part of the code runs only if the script is invoked directly
    instead of being imported from a different module.

    This way this script provides both - an executable and a "library".
    """

    # Create an ArgumentParer with a description of what our script does.
    parser = argparse.ArgumentParser(description='Get the top 10 links of the day from a subreddit.')

    # We add our positional argument, the first argument is the attribute we can access
    # after parsing our arguments, then we add a help text and define the type.
    parser.add_argument('subreddit', help='A subreddit on Reddit', type=str)

    # We add our second, positional, but required argument for the output path
    parser.add_argument('-o', '--output', help='Output path', type=str, required=True)

    # We parse the user's input and check if all the required arguments were supplied
    args = parser.parse_args()

    # We initialize an "r" instance with no value, to silence the IDE warning.
    r = None

    # If we've gotten here, then the required arguments were supplied.
    # We then initialize our class with the subreddit argument, and check
    # if it doesn't throw an exception that the subreddit doesn't exist.
    # If it doesn't, we handle the exception gracefully.
    try:
        r = RedditScraper(args.subreddit)
    except RedditScraperResponseException as e:
        handle_exception(e)

    # Ok, it seems that the provided subreddit was fine, and we can try to write
    # the CSV file. Of course, we check if an exception wasn't thrown while
    # trying to write.
    try:
        r.write(args.output)
    except RedditScraperWriteException as e:
        handle_exception(e)

    # Everything should be fine by now, so we write a message to let the user know.
    print('Success!')
