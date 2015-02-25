"""
test_ssl_certificate.py

Copyright 2012 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import os

from nose.plugins.attrib import attr

from w3af import ROOT_PATH
from w3af.plugins.tests.helper import PluginTest, PluginConfig
from w3af.core.data.url.tests.helpers.ssl_daemon import SSLServer
from w3af.core.controllers.misc.get_unused_port import get_unused_port


class TestSSLCertificate(PluginTest):

    PORT = get_unused_port()
    local_target_url = 'https://localhost:%s/' % PORT

    remote_url = 'https://www.yandex.com/'
    EXPECTED_STRINGS = ('yandex.ru', 'Moscow', 'RU', 'yandex')

    _run_configs = {
        'cfg': {
            'target': None,
            'plugins': {
                'audit': (PluginConfig('ssl_certificate'),),
            }
        }
    }

    def test_ssl_certificate_local(self):
        # Start the HTTPS server
        certfile = os.path.join(ROOT_PATH, 'plugins', 'tests', 'audit',
                                'certs', 'invalid_cert.pem')
        s = SSLServer('localhost', self.PORT, certfile)
        s.start()

        cfg = self._run_configs['cfg']
        self._scan(self.local_target_url, cfg['plugins'], debug=True)

        s.stop()

        #
        #   Check the vulnerability
        #
        vulns = self.kb.get('ssl_certificate', 'invalid_ssl_cert')

        self.assertEquals(1, len(vulns))

        # Now some tests around specific details of the found vuln
        vuln = vulns[0]
        self.assertEquals('Invalid SSL certificate', vuln.get_name())
        self.assertEquals(self.local_target_url, str(vuln.get_url()))

    @attr('internet')
    def test_ssl_certificate_yandex(self):
        cfg = self._run_configs['cfg']
        self._scan(self.remote_url, cfg['plugins'])

        #
        #   Check the certificate information
        #
        info = self.kb.get('ssl_certificate', 'certificate')
        self.assertEquals(1, len(info))

        # Now some tests around specific details of the found info
        info = info[0]
        self.assertEquals('SSL Certificate dump', info.get_name())
        self.assertEquals(self.remote_url, str(info.get_url()))

        for estring in self.EXPECTED_STRINGS:
            self.assertIn(estring, info.get_desc())
