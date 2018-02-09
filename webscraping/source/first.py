# Here we're borrowing a bunch of work
# other people have already done so we
# don't have to!
#
# Here we import the whole package
import bs4
import requests
import sys

# and here we're borrowing specific
# things from the packages
from os.path import splitext, join
from os import getcwd


# The "def" keyword declares a function
# And an empty parentheses, since we don't
# need any arguments. Unlike other languages,
# it doesn't even have to be called "main".
def main():
    # Send a GET request to imgur.com
    response = requests.get('https://imgur.com/')

    # Initialize the BeatifulSoup parser with the HTML content
    # which imgur.com sent back and with the default HTML parser.
    # It's slower than other alternatives, but it's perfectly enough for now
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    # Get all elements with the class "image-list-link"
    # The keyword argument for querying a css class in "class_"
    # since "class" is a reserved keyword in python.
    links = soup.find_all(class_='image-list-link')

    # Since the "src" attributes are missing the protocol in their URL
    # We'll just add it ourselves.
    prefix = 'https:'

    # We're about to iterate over all of the links we encountered.
    # The enumerate function returns a generator with 2-item tuples
    # where the first item is the current index.
    # 0-indexed, because we're not lua :)
    #
    # And python supports variable unpacking like this:
    #     one, two = (1, 2)
    #
    # And we are doing just that in the for-loop declaration
    for i, el in enumerate(links):
        # Find the first "img" tag we encounter amont the "a" elements children.
        # And get the "src" attribute with the square bracket notation,
        # just like we would on a regular dictionary.
        src = el.find('img')['src']

        # We separate the extension from the rest and, once again, unpack the result.
        base, ext = splitext(src)

        # Now we construct a URL using our predefined index from before,
        # the first part of the URL (sans the last character) and glue
        # the extension to the end, and perform a request for that URL
        image = requests.get(prefix + base[:-1] + ext)

        # the "with" keyword indicates a context manager. You can find
        # a good explanation in the Python documentation, but, in a nutshell
        # what it does is prevents us from forgetting to close the file
        # object we're about to open, since it only remains opened in the
        # context of the with statement.
        #
        # As the arguments to open - we give our current loop index + the extension
        # as the file name located in the current working directory.
        #
        # We use os.path.join(), so our code is OS-agnostic
        # (Since path separators for windows are backslashes, while
        # separators for linux and macOS are forward slashes)
        #
        # We create the file by "opening" in writable binary mode, and
        # pass it into the context manager as the reference "f".
        with open(join(getcwd(), str(i) + ext), 'wb') as f:
            # And we just write the binary content of the response
            # to the file, and since there are no further statements
            # within this context manager, it will be closed.
            f.write(image.content)


# Double-underscore variables or "dunders" as they're called in the
# python world, have a very special meaning everywhere - in classes,
# functions and modules, but I'll leave that for another time.
if __name__ == '__main__':
    # We're using a try-except construct, because we're pretty sure
    # something will go wrong at some point.
    try:
        # Run our function and cross our fingers.
        main()
    # We're only handling the KeyboardInterrupt exception, which occures
    # When Ctrl-C is pressed, because if we would catch every exception,
    # finding bugs in the code would get really tedious.
    except KeyboardInterrupt:
        # We notify the user that the party is over,
        print('Exiting...')

        # And exit the program.
        #
        # You can, optionally supply a status code to exit(), but the
        # default is 0.
        sys.exit()
