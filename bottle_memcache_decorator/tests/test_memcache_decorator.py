#!/usr/bin/env python
"""Unittest for bottle_memcache_decorator"""
import time
import unittest

import bottle
from bottle import request, PluginError
from bottle.ext import memcache
from bottle_memcache_decorator import MemcacheDecoratorPlugin

class MemcacheDecoratorPluginTest(unittest.TestCase):

    def setUp(self):
        self.app = bottle.Bottle(catchall=False)
        self.keyword = 'mc'

        # install memcache plugin
        memcache_plugin = memcache.MemcachePlugin(keyword=self.keyword)
        self.app.install(memcache_plugin)

        self.results = dict()

    def tearDown(self):
        self.results = None

        @self.app.get('/flush_memcache')
        def test(mc):
            mc.flush_all()

        self._request_path('/flush_memcache')

    def _request_path(self, path, query_string='', method='GET'):
        req = {
            'PATH_INFO': path,
            'QUERY_STRING': query_string,
            'REQUEST_METHOD': method
        }
        return self.app(req, lambda x, y: None)

    def _install_plugin(self, *args, **kwargs):
        # install the memcache decorator
        memcache_decorator_plugin = MemcacheDecoratorPlugin(
                                memcache_keyword=self.keyword, *args, **kwargs)
        self.app.install(memcache_decorator_plugin)

    def test_get_from_memcache(self):
        """Check if the returned result was picked from memcache"""

        @self.app.get('/test')
        def test(mc):
            return "%f" % time.time()

        self._install_plugin()
        # get fresh result and set to memcache
        res1 = self._request_path('/test')[0]

        # get memcached result
        res2 = self._request_path('/test')[0]

        # both res1 and res2 must be the same
        self.assertEqual(res1, res2)

    def test_set_wildcards(self):
        """
        Check if key stored in memcache is unique
        based on route wildcards
        """

        @self.app.get('/test_wildcards/<id:int>')
        def test(mc, id):
            self.results[id] = "%d:%f" % (id, time.time())
            return self.results[id]

        self._install_plugin()

        res1 = self._request_path('/test_wildcards/1')[0]
        res2 = self._request_path('/test_wildcards/2')[0]

        self.assertNotEqual(res1, res2)
        self.assertEqual(res1, self.results[1].encode())
        self.assertEqual(res2, self.results[2].encode())

    def test_set_query_params(self):
        """
        Check if key stored in memcache is unique
        based on query parameters
        """

        @self.app.get('/test_q_params')
        def test(mc):
            param = request.query.get('param', None)

            self.results[param] = "%s:%f" % (param, time.time())
            return self.results[param]

        self._install_plugin()

        res1 = self._request_path('/test_q_params', 'param=a')[0]
        res2 = self._request_path('/test_q_params', 'param=b')[0]

        self.assertNotEqual(res1, res2)
        self.assertEqual(res1, self.results['a'].encode())
        self.assertEqual(res2, self.results['b'].encode())

    def test_expire_time(self):
        """Test router argument set for memcache key expire time"""

        @self.app.get('/test', mc_expire_time=1)
        def test(mc):
            return "%f" % time.time()

        self._install_plugin()
        # get fresh result and set to memcache
        res1 = self._request_path('/test')[0]

        # get memcached result
        res2 = self._request_path('/test')[0]

        time.sleep(1)

        # memcache result must be expired after 1 second
        # get fresh result and set to memcache
        res3 = self._request_path('/test')[0]

        # both res1 and res2 must be the same
        self.assertEqual(res1, res2)

        # res3 must be different from res1 and res2
        self.assertNotEqual(res1, res3)

    def test_compress_level(self):
        """Test router argument set for memcache compression level"""

        @self.app.get('/test', mc_compress_level=1)
        def test(mc):
            return "%f" % time.time()

        self._install_plugin()
        # get fresh result and set to memcache
        res1 = self._request_path('/test')[0]

        # get memcached result
        res2 = self._request_path('/test')[0]

        # both res1 and res2 must be the same
        self.assertEqual(res1, res2)

    def test_install_same_plugin_conflicts(self):
        """
        Installing the plugin twice with the same arguments
        and check if raises PluginError
        """
        self._install_plugin()
        self.assertRaises(PluginError, self._install_plugin, memcache_expire_time_keyword='mc_expire_time')

if __name__ == '__main__':
    unittest.main()