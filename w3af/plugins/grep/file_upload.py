'''
file_upload.py

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
from lxml import etree

import core.data.kb.knowledge_base as kb

from core.controllers.plugins.grep_plugin import GrepPlugin
from core.data.bloomfilter.scalable_bloom import ScalableBloomFilter
from core.data.kb.info import Info


FILE_INPUT_XPATH = ".//input[translate(@type,'FILE','file')='file']"


class file_upload(GrepPlugin):
    '''
    Find HTML forms with file upload capabilities.

    :author: Andres Riancho (andres.riancho@gmail.com)
    '''

    def __init__(self):
        GrepPlugin.__init__(self)

        # Internal variables
        self._already_inspected = ScalableBloomFilter()
        self._file_input_xpath = etree.XPath(FILE_INPUT_XPATH)

    def grep(self, request, response):
        '''
        Plugin entry point, verify if the HTML has a form with file uploads.

        :param request: The HTTP request object.
        :param response: The HTTP response object
        :return: None
        '''
        url = response.get_url()

        if response.is_text_or_html() and not url in self._already_inspected:

            self._already_inspected.add(url)
            dom = response.get_dom()

            # In some strange cases, we fail to normalize the document
            if dom is not None:

                # Loop through file inputs tags
                for input_file in self._file_input_xpath(dom):
                    msg = 'The URL: "%s" has form with file upload capabilities.'
                    msg = msg % url
                    
                    i = Info('File upload form', msg, response.id,
                             self.get_name())
                    i.set_url(url)
                    to_highlight = etree.tostring(input_file)
                    i.add_to_highlight(to_highlight)
                    
                    self.kb_append_uniq(self, 'file_upload', i, 'URL')

    def get_long_desc(self):
        '''
        :return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin greps every page for forms with file upload capabilities.
        '''
