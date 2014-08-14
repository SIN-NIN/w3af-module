# -*- coding: utf8 -*-
"""
form.py

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

"""
from w3af.core.data.dc.generic.form import Form
from w3af.core.data.parsers.encode_decode import urlencode
from w3af.core.data.parsers.url import parse_qs
from w3af.core.data.parsers.utils.form_params import FormParameters


class URLEncodedForm(Form):
    """
    This class represents an HTML form.

    :author: Andres Riancho (andres.riancho@gmail.com) |
             Javier Andalia (jandalia =at= gmail.com)
    """
    ENCODING = 'application/x-www-form-urlencoded'

    AVOID_FILLING_FORM_TYPES = {'checkbox', 'radio', 'select'}
    AVOID_STR_DUPLICATES = {FormParameters.INPUT_TYPE_CHECKBOX,
                            FormParameters.INPUT_TYPE_RADIO,
                            FormParameters.INPUT_TYPE_SELECT}

    @staticmethod
    def is_urlencoded(headers):
        conttype, header_name = headers.iget('content-type', '')
        return URLEncodedForm.ENCODING in conttype.lower()

    @staticmethod
    def can_parse(post_data):
        try:
            parse_qs(post_data)
        except:
            return False
        else:
            return True

    @classmethod
    def from_postdata(cls, headers, post_data):
        if not URLEncodedForm.is_urlencoded(headers):
            raise ValueError('Request is not %s.' % URLEncodedForm.ENCODING)

        if not URLEncodedForm.can_parse(post_data):
            raise ValueError('Failed to parse post_data as Form.')

        data = parse_qs(post_data)
        urlencoded_form = cls()
        urlencoded_form.update(data.items())

        return urlencoded_form

    def __str__(self):
        """
        This method returns a string representation of the Form object.

        Please note that if the form has radio/select/checkboxes the
        first value will be put into the string representation and the
        others will be lost.

        :see: Unittest in test_form.py
        :return: string representation of the Form object.
        """
        d = dict()
        d.update(self.items())
        d.update(self.get_form_params().get_submit_map())

        for key in d:
            key_type = self.get_parameter_type(key, default=None)
            if key_type in self.AVOID_STR_DUPLICATES:
                d[key] = d[key][:1]

        return urlencode(d, encoding=self.encoding, safe='')

    def get_type(self):
        return 'URL encoded form'

