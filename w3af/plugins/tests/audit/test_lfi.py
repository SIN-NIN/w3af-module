'''
test_lfi.py

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
'''

from plugins.tests.helper import PluginTest, PluginConfig


class TestLFI(PluginTest):

    target_url = 'http://moth/w3af/audit/local_file_inclusion/index.html'

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {
                'audit': (PluginConfig('lfi'),),
                'crawl': (
                    PluginConfig(
                        'web_spider',
                        ('only_forward', True, PluginConfig.BOOL)),
                )

            }
        }
    }

    def test_found_lfi(self):
        # Run the scan
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        # Verify the specifics about the vulnerabilities
        EXPECTED = [
            ('lfi_1.php', 'file'),
            # FIXME: ('lfi_2.php', 'file'), null-bytes don't work in latest PHP anymore
            # need to find a new technique that (hopefully) also works in old PHP versions
            ('trivial_lfi.php', 'file'),
        ]

        # Assert the general results
        vulns = self.kb.get('lfi', 'lfi')
        self.assertEquals(len(EXPECTED), len(vulns), vulns)
        self.assertEquals(
            all(["Local file inclusion vulnerability" == v.get_name(
            ) for v in vulns]),
            True)

        self.assertEqual(set(EXPECTED),
                         set([(v.get_url().get_file_name(), v.get_mutant().get_var()) for v in vulns]))
