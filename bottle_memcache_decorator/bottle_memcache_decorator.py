#!/usr/bin/env python
"""
This bottle-memcache-decorator plugin adds a memcache decorator in your Bottle
application. It automatically stores the route result to memcache for routes
where the bottle-memcache plugin is enabled.

The bottle-memcache plugin is required to be installed before this plugin.

The plugin can read extra options per route. This extra options can be defined
as route arguments. These arguments are defined during the initialization of this plugin,
although I will explain their functionality with their default values:
    mc_expire_time: set the memcache key/value expire time for a route, 0 means never expire
    mc_compress_level: set the memcache compression level for a route, 0-9 with 0 means no compression

Usage Example::

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
                            memcache_expire_time_keyword='mc_expire_time',
                            memcache_compress_level_keyword='mc_compress_level')
    app.install(memcache_decorator_plugin)

    # for example in this route we will set the expire time = 3600 sec
    # and compression level = 3
    @app.get('/:name', mc_expire_time=3600, mc_dec_compress_level=3)
    def show(name, mc):
        # your code here

        return result


Copyright (c) 2013, Chris Ziogas
License: MIT (see LICENSE for details)
"""

import inspect
import bottle
from bottle import request

# PluginError is defined to bottle >= 0.10
if not hasattr(bottle, 'PluginError'):
    class PluginError(bottle.BottleException):
        pass
    bottle.PluginError = PluginError

HEADERS_FOR_UNIQUE_NAMING = ['range']

class MemcacheDecoratorPlugin(object):
    """
    Auto Memcache decorator
    It is applied only in the functions where a Memcache argument is set
    """

    name = 'memcache_decorator'
    api = 2

    def __init__(self, memcache_keyword='mc',
            memcache_expire_time_keyword='mc_expire_time',
            memcache_compress_level_keyword='mc_compress_level'):
        '''
        @param memcache_keyword: Keyword used by bottle_memcache.py
            to inject memcache connection in a route
        @param memcache_expire_time_keyword: keyword used set the memcache key expire time
            for a route, 0 means never expire
        @param memcache_compress_level_keyword: keyword used set the memcache compression level
            for a route, 0-9 with 0 means no compression
        '''
        self.memcache_keyword = memcache_keyword
        self.memcache_expire_time_keyword = memcache_expire_time_keyword
        self.memcache_compress_level_keyword = memcache_compress_level_keyword

    def setup(self, app):
        for other in app.plugins:
            if not isinstance(other, MemcacheDecoratorPlugin):
                continue
            if other.memcache_expire_time_keyword == self.memcache_expire_time_keyword \
                    or other.memcache_compress_level_keyword == self.memcache_compress_level_keyword:
                raise bottle.PluginError("Found another memcache_decorator plugin with "\
                        "conflicting settings (non-unique keyword).")

    def apply(self, callback, context):
        """
        Only apply this plugin if route is enabled for memcache use
        """
        # hack to support bottle v0.9.x
        if bottle.__version__.startswith('0.9'):
            conf = context['config']
            app = context['app']
            _callback = context['callback']
        else:
            conf = context.config
            app = context.app
            _callback = context.callback

        memcache_expire_time = conf.get(self.memcache_expire_time_keyword, 0)
        memcache_compress_level = conf.get(self.memcache_compress_level_keyword, 0)

        # don't load this plugin in case bottle-memcache
        # is not used for this route
        # @NOTE: this check can also be performed inside the wrapper func
        args = inspect.getargspec(_callback)[0]
        if self.memcache_keyword not in args:
            return callback

        def _build_unique_memcache_name(**kwargs):
            """
            The memcache key must be unique
            and for that to happen we must consider:
                a) the url wildcards
                b) the query items
            """
            url_params = {}

            # set default key for memcache store
            memcache_key = context.name or context.rule

            # consider the url wildcards
            for param, param_type in app.router.builder[context.rule]:
                if param and param in kwargs:
                    url_params[param] = kwargs[param]

            # consider the query items
            for items in request.query.items():
                url_params[items[0]] = items[1]

            # consider some headers that may affect the result
            for header in HEADERS_FOR_UNIQUE_NAMING:
                if header in request.headers:
                    url_params[header] = request.headers[header]

            # get a unique memcache key based on the user request
            if url_params:
                memcache_key = app.get_url(context.rule, **url_params)

            # return str(hash(memcache_key))
            return memcache_key

        def wrapper(*args, **kwargs):
            # get key for memcache store
            memcache_key = _build_unique_memcache_name(**kwargs)

            # get memcache object
            mc = kwargs[self.memcache_keyword]

            # get data from memcache if exist
            output = mc.get(memcache_key)

            # if nothing found in memcache
            if not output:
                # run the function
                output = callback(*args, **kwargs)

                # store data in memcache
                mc.set(memcache_key, output, memcache_expire_time, memcache_compress_level)

            return output
        return wrapper