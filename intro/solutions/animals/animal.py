class Animal(object):

    def __init__(self, name):
        super(Animal,self).__init__(name)
        self.name = name

    def say(self):
        print('...')