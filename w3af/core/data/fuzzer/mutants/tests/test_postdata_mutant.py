'''
test_postdata_mutant.py

Copyright 2006 Andres Riancho

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
import unittest

from core.data.parsers.url import URL
from core.data.fuzzer.mutants.postdata_mutant import PostDataMutant
from core.data.dc.form import Form
from core.data.request.HTTPPostDataRequest import HTTPPostDataRequest


class TestPostDataMutant(unittest.TestCase):

    def setUp(self):
        self.payloads = ['abc', 'def']
        self.fuzzer_config = {}

    def test_found_at(self):
        form = Form()
        form.add_input([("name", "username"), ("value", "")])
        form.add_input([("name", "address"), ("value", "")])

        freq = HTTPPostDataRequest(URL('http://www.w3af.com/?id=3'), dc=form,
                                   method='PUT')
        m = PostDataMutant(freq)
        m.set_var('username')

        expected = '"http://www.w3af.com/?id=3", using HTTP method PUT. '\
                   'The sent post-data was: "username=&address=" '\
                   'which modifies the "username" parameter.'
        self.assertEqual(m.found_at(), expected)

    def test_mutant_creation(self):
        form = Form()
        form.add_input([("name", "username"), ("value", "")])
        form.add_input([("name", "address"), ("value", "")])

        freq = HTTPPostDataRequest(URL('http://www.w3af.com/?id=3'), dc=form,
                                   method='PUT')

        created_mutants = PostDataMutant.create_mutants(
            freq, self.payloads, [],
            False, self.fuzzer_config)

        expected_dc_lst = [Form(
            [('username', ['abc']), ('address', ['Bonsai Street 123'])]),
            Form([('username', [
                   'def']), ('address', ['Bonsai Street 123'])]),
            Form([('username', [
                   'John8212']), ('address', ['abc'])]),
            Form([('username', ['John8212']), ('address', ['def'])])]

        created_dc_lst = [i.get_dc() for i in created_mutants]

        self.assertEqual(created_dc_lst, expected_dc_lst)

        self.assertEqual(created_mutants[0].get_var(), 'username')
        self.assertEqual(created_mutants[0].get_var_index(), 0)
        self.assertEqual(created_mutants[0].get_original_value(), '')
        self.assertEqual(created_mutants[2].get_var(), 'address')
        self.assertEqual(created_mutants[2].get_var_index(), 0)
        self.assertEqual(created_mutants[2].get_original_value(), '')

        self.assertTrue(
            all(isinstance(m, PostDataMutant) for m in created_mutants))
        self.assertTrue(
            all(m.get_method().startswith('PUT') for m in created_mutants))

    def test_mutant_creation_file(self):
        form = Form()
        form.add_input([("name", "username"), ("value", "default")])
        form.add_file_input([("name", "file_upload")])

        freq = HTTPPostDataRequest(URL('http://www.w3af.com/upload'), dc=form,
                                   method='POST')

        payloads = [file(__file__),]
        created_mutants = PostDataMutant.create_mutants(
            freq, payloads, ['file_upload', ],
            False, self.fuzzer_config)

        self.assertEqual(len(created_mutants), 1, created_mutants)
        
        mutant = created_mutants[0]
        
        self.assertIsInstance(mutant.get_dc()['file_upload'][0], file)
        self.assertEqual(mutant.get_dc()['username'][0], 'default')
        
