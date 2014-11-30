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

PRODUCT_FISCAL_TYPE = [
    ('service', u'Serviço'),('Desconhecido','Desconhecido'),('SimplesNacional','SimplesNacional')
]



class res_partner(osv.osv):
    _inherit="res.partner"
   
    _columns = {'is_nfeio':fields.boolean('Is Nfeio'),
                'cnae_main_id': fields.many2one('l10n_br_account.cnae', u'CNAE Primário'),
                'cnae_secondary_ids': fields.many2many('l10n_br_account.cnae', 'res_partner_l10n_br_account_cnae',
                'company_id', 'cnae_id', u'CNAE Segundários'),
                'naturezaJuridica':fields.char('Natureza Juridica'),
                'fiscal_type': fields.selection(PRODUCT_FISCAL_TYPE, 'Tipo Fiscal'), #regimeTributario
                'situacaoCadastral':fields.char('Situacao Cadastral'),
                'dataSituacaoCadastral':fields.datetime('Data Situacao Cadastral'),  
                'dataCadastroMei':fields.datetime('Data CadastroMei'),
                'dataAbertura':fields.datetime('Data Abertura'),
                'nfeio_fetch_date':fields.datetime('Data Pesquisa'),
                   }
    

    def onchange_mask_cnpj_cpf(self, cr, uid, ids, is_company, cnpj_cpf):
        result = super(res_partner,self).onchange_mask_cnpj_cpf( cr, uid, ids, is_company, cnpj_cpf)
        if cnpj_cpf:
            print "ids....................",ids
            company_id = False
            if ids: 
                company_id = self.browse(cr, uid, ids[0]).company_id.id
            if not company_id:
                company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
            client_dict = self.pool.get('res.company').client_dict(cr, uid, cnpj_cpf, company_id, context=None)
            result['value'].update(client_dict)
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
    
    
                
        
            