from animals.animal import Animal

class Dog(Animal):

    def __init__(self, name):
        super(Animal,self).__init__()

    def bark(self):
        print('woof!')