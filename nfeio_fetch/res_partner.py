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

from openerp.osv import osv, fields
import requests
import re

PRODUCT_FISCAL_TYPE = [
    ('service', u'Serviço'),('Desconhecido',u'Desconhecido'),('SimplesNacional',u'SimplesNacional'),('MEI','MEI')
]



class res_partner(osv.osv):
    _inherit="res.partner"
   
    _columns = {'is_nfeio':fields.boolean(u'Is Nfeio'),
                'nfeio_search':fields.boolean(u'Nfeio Search',help="If this field is not True CNPJ/CPF will not be searched with NFEIO"),
                'cnae_main_id': fields.many2one('l10n_br_account.cnae', u'CNAE Primário'),
                'cnae_secondary_ids': fields.many2many('l10n_br_account.cnae', 'res_partner_l10n_br_account_cnae',
                'company_id', 'cnae_id', u'CNAE Segundários'),
                'naturezaJuridica':fields.char(u'Natureza Juridica'),
                'fiscal_type': fields.selection(PRODUCT_FISCAL_TYPE, u'Tipo Fiscal'), #regimeTributario
                'situacaoCadastral':fields.char(u'Situacao Cadastral'),
                'dataSituacaoCadastral':fields.datetime(u'Data Situacao Cadastral'),  
                'dataCadastroMei':fields.datetime(u'Data CadastroMei'),
                'dataAbertura':fields.datetime(u'Data Abertura'),
                'nfeio_fetch_date':fields.datetime(u'Data Pesquisa'),
                   }
    _defaults={
               'nfeio_search':True
               }
    
    
    def onchange_mask_cnpj_cpf(self, cr, uid, ids, is_company, cnpj_cpf, nfeio_search):
        result = super(res_partner, self).onchange_type(cr, uid, ids, is_company)
        if cnpj_cpf:
            val = re.sub('[^0-9]', '', cnpj_cpf)
            if is_company and len(val) == 14:
                cnpj_cpf = "%s.%s.%s/%s-%s"\
                % (val[0:2], val[2:5], val[5:8], val[8:12], val[12:14])
            elif not is_company and len(val) == 11:
                cnpj_cpf = "%s.%s.%s-%s"\
                % (val[0:3], val[3:6], val[6:9], val[9:11])
            result['value'].update({'cnpj_cpf': cnpj_cpf})

        if cnpj_cpf:
            company_id = False
            if ids: 
                company_id = self.browse(cr, uid, ids[0]).company_id.id
            if not company_id:
                company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
            client_dict = {'value':{'is_company_selection':'j'}}
            if is_company and nfeio_search:
                client_dict = self.pool.get('res.company').client_dict(cr, uid, cnpj_cpf, company_id, context=None)
            
            if client_dict:
                result['value'].update(client_dict)
            else:
                result['value'].update({'nfeio_search':False})
        return result
    

    def zip_search(self, cr, uid, ids, context=None):
        company_obj = self.pool.get('res.company')
        for partner in self.browse(cr, uid, ids):
            zip = partner.zip
           # api = company_obj.browse(cr, uid, partner.company_id.id).nfe_api
            if partner.company_id:
                company_id = partner.company_id.id 
            else:
                company_id = self.pool.get('res.users').browse(cr,uid, uid).company_id.id
            address_dict = self.pool.get('res.company').address_dict(cr, uid, zip, company_id, context=context)
            self.write(cr, uid, ids, address_dict, context=context)
        return True
    
    
    def cnpj_search(self, cr, uid, ids, context=None):
        company_obj = self.pool.get('res.company')
        for partner in self.browse(cr, uid, ids):
            cnpj = partner.cnpj_cpf
            if partner.company_id:
                company_id = partner.company_id.id 
            else:
                company_id = self.pool.get('res.users').browse(cr,uid, uid).company_id.id
            client_dict = self.pool.get('res.company').client_dict(cr, uid, cnpj, company_id, context=context)
            self.write(cr, uid, ids, client_dict, context=context)
        return True
    
    
                
        
            