# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen Brasil
#    Copyright (C) Thinkopen Solutions Brasil (<http://www.tkobr.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Integration with http://app.nfe.io',
    'version': '0.001',
    'category': 'Integration',
    'sequence': 38,
    'complexity': 'normal',
    'description': ''' This module does integration with http://app.nfe.io to be able to search brazilian states, cities
''',
    'author': 'ThinkOpen Solutions Brasil',
    'website': 'http://www.tkobr.com',
    'images': ['images/oerp61.jpeg',
              ],
    'depends': ['base',
                'l10n_br_base',
               ],
    'data': [
             'res_company_view.xml',
             'res_partner_view.xml',
             ],
    'init': [],
    'demo': [],
    'update': [],
    'test': [], #YAML files with tests
    'installable': True,
    'application': False,
    'auto_install': False, #If it's True, the modules will be auto-installed when all dependencies are installed
    'certificate': '',
}
