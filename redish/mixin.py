import redish.proxy

def Proxied(key):
    """generate a property, which is a pair of closures over the named key"""
    def get_proxied(instance, key=key):
        return instance._keyspace[key]

    def set_proxied(instance, val, key=key):
        instance._keyspace[key] = val

    return property(fget=get_proxied, fset=set_proxied)

class RedisMixin(object):
    """A mixin that allows your class to use redish keyspaced proxies as
    a backing store for member variables.  To use, define a __keyspace__
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
    def _keyspace(self):
        """when attribute access occurs, this method "memoizes" the keyspaced
        proxy, on the assumption that by the time you start messing about
        with properties, your __keyspace__ method is callable
        """
        self.__keyspace = getattr(self, '__keyspace', None) or self._proxy.keyspace(self.__keyspace__())
        return self.__keyspace

class Test(RedisMixin):
    __keyspace__ = lambda self: "test:%d:%%s" % self.id
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
