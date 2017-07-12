#a stub module to have a group of functions
class test_module_1(object):
    name = None
    def __init__(self, name):
        self.name= name
    def log(self, info):
        print('{}{}'.format('test_module_1: ',info))
    def function_1(self,*args, **kwargs):

        self.log('args: '+'{}'.format(args))
        self.log('kwargs:')
        for k in kwargs.keys():
            self.log('\t{}:{}'.format(k,kwargs[k]))


if __name__ == "__main__":
    m = test_module_1()
    m.log( 'hello world')
    m.function_1(2,3)
    m.function_1(1, 2,3, a=1, b='c')