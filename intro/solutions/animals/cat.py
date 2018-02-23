from animals.animal import Animal

class Cat(Animal):
    
    def __init__(self, name):
        super(Animal,self).__init__()

    def meow(self):
        print('meow')