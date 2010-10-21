import redish.proxy

def Proxied(key):
    """generate a property, which is a pair of closures over the named key"""
    def get_proxied(instance, key=key):
        return instance._nsproxy[key]

    def set_proxied(instance, val, key=key):
        instance._nsproxy[key] = val

    return property(fget=get_proxied, fset=set_proxied)

class RedisMixin(object):
    """A mixin that allows your class to use redish namespaced proxies as
    a backing store for member variables.  To use, define a __namespace__
    lambda function that returns the namespace for this object, and store the
    master proxy in self._proxy


    Example:
    class Test(RedisMixin):
        __namespace__ = lambda self: "test:%d:%%s" % self.id
        foo = Proxied('foo')
        bar = Proxied('bar')
        baz = Proxied('baz')

        def __init__(self, proxy, id):
            self._proxy = proxy
            self.id = id

    proxy = redish.proxy.Proxy(db=4)
    t = Test(proxy, 1)
    t.foo = 1
    t.bar = ['hello', 'goodbye']
    t.baz = dict(a=1, b=2)

    proxy.get('test:1:foo')           -> 1
    proxy.lrange('test:1:bar', 0, -1) -> ['hello', 'goodbye']
    proxy.hgetall('test:1:baz')       -> {'a': '1', 'b': '2'}
    """
    @property
    def _nsproxy(self):
        """when attribute access occurs, this method "memoizes" the namespaced
        proxy, on the assumption that by the time you start messing about
        with properties, your __namespace__ method is callable
        """
        self.__nsproxy = getattr(self, '__nsproxy', None) or self._proxy.namespaced(self.__namespace__())
        return self.__nsproxy

class Test(RedisMixin):
    __namespace__ = lambda self: "test:%d:%%s" % self.id
    foo = Proxied('foo')
    bar = Proxied('bar')
    baz = Proxied('baz')

    def __init__(self, proxy, id):
        self._proxy = proxy
        self.id = id

if __name__=='__main__':
    proxy = redish.proxy.Proxy(db=4)
    t = Test(proxy, 1)
    t.foo = 1
    t.bar = ['hello', 'goodbye']
    t.baz = dict(a=1, b=2)

    print proxy.get('test:1:foo')
    print proxy.lrange('test:1:bar', 0, -1)
    print proxy.hgetall('test:1:baz')
