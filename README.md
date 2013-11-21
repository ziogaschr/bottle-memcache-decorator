bottle-memcache-decorator [![Build Status](https://travis-ci.org/ziogaschr/bottle-memcache-decorator.png)](https://travis-ci.org/ziogaschr/bottle-memcache-decorator)
=========================

This bottle-memcache-decorator plugin adds a memcache decorator in your Bottle
application. It automatically stores the route result to memcache for routes
where the bottle-memcache plugin is enabled.


Required
===============

The bottle-extras and bottle_memcache plugins are required to be installed before this plugin.


Installation
===============

Install with one of the following commands::

    $ pip install bottle-memcache-decorator
    $ easy_install bottle-memcache-decorator

or download the latest version from github::

    $ git clone git://github.com/ziogaschr/bottle-memcache-decorator.git
    $ cd bottle-memcache-decorator
    $ python setup.py install


Usage
===============

    import bottle
    from bottle.ext import memcache
    from bottle_memcache_decorator import MemcacheDecoratorPlugin

    app = bottle.Bottle()

    keyword = 'mc'

    # install memcache plugin
    memcache_plugin = memcache.MemcachePlugin(keyword=keyword)
    app.install(memcache_plugin)

    # install the memcache decorator
    memcache_decorator_plugin = MemcacheDecoratorPlugin(
                            memcache_keyword=keyword,
                            memcache_expire_time='mc_expire_time',
                            memcache_compress_level_keyword='mc_compress_level')
    app.install(memcache_decorator_plugin)

    # for example in this route we will set the expire time = 3600 sec
    # and compression level = 3
    @app.get('/:name', mc_expire_time=3600, mc_dec_compress_level=3)
    def show(name, mc):
        # your code here

        return result

    if __name__ == '__main__':
        run(app, host='0.0.0.0', port=8080, debug=True)


Configuration
=============

    MemcacheDecoratorPlugin(
        memcache_keyword='mc',
        memcache_expire_time='mc_expire_time',
        memcache_compress_level_keyword='mc_compress_level')

**memcache_keyword**: is the keyword set/used for the memcache plugin

**memcache_expire_time**: defines the router argument responsible for setting the memcache expire time

**memcache_compress_level_keyword**: defines the router argument responsible for setting the memcache compression level