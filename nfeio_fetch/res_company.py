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


from openerp.osv import orm, osv, fields
from datetime import datetime
import requests
import logging
_logger = logging.getLogger(__name__)


PRODUCT_FISCAL_TYPE = [
    ('service', u'Serviço'),('Desconhecido','Desconhecido'),('SimplesNacional','SimplesNacional'),('MEI','MEI')
]



class L10n_brAccountCNAE(orm.Model):
    _name = 'l10n_br_account.cnae'
    _description = 'Cadastro de CNAE'
    _columns = {
        'code': fields.char(u'Código', size=16, required=True),
        'name': fields.char(u'Descrição', size=64, required=True),
        'version': fields.char(u'Versão', size=16, required=True),
        'parent_id': fields.many2one('l10n_br_account.cnae', 'CNAE Pai'),
        'child_ids': fields.one2many(
            'l10n_br_account.cnae', 'parent_id', 'CNAEs Filhos'),
        'internal_type': fields.selection(
            [('view', u'Visualização'), ('normal', 'Normal')],
            'Tipo Interno', required=True),
    }
    _defaults = {
        'internal_type': 'normal'
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' - ' + name
            res.append((record['id'], name))
        return res



class res_company(osv.osv):
    _inherit="res.company"
    _columns = {
            'is_nfeio':fields.boolean('is_nfeio ?'),
            'cnae_main_id': fields.many2one('l10n_br_account.cnae', u'CNAE Primário'),
            'cnae_secondary_ids': fields.many2many('l10n_br_account.cnae', 'res_company_l10n_br_account_cnae',
            'company_id', 'cnae_id', u'CNAE Segundários'),
            'nfe_api':fields.char('NFEIO API'),
            
            'naturezaJuridica':fields.char('Natureza Juridica'),
            'fiscal_type': fields.selection(PRODUCT_FISCAL_TYPE, 'Tipo Fiscal'), #regimeTributario
            'dataSituacaoCadastral':fields.datetime('Data Situacao Cadastral'),  
            'situacaoCadastral':fields.char('Situacao Cadastral'), 
            'dataCadastroMei':fields.datetime('Data CadastroMei'), 
            'dataAbertura':fields.datetime('Data Abertura'),
            'nfeio_fetch_date':fields.datetime('Data Pesquisa'),
                    }
    
    
    def onchange_mask_cnpj_cpf(self, cr, uid, ids, cnpj_cpf):
        result = super(res_company, self).onchange_mask_cnpj_cpf( cr, uid, ids, cnpj_cpf)
        if cnpj_cpf:
            company_id = ids and ids[0] or False
            client_dict = self.client_dict( cr, uid, cnpj_cpf, company_id,  context=None)
            # update value returned by super method
            result['value'].update(client_dict)
        return result
    
    
    def validate_api(self, cr, uid, ids, context=None):
        for company in self.browse(cr, uid, ids):
            url = 'http://open.nfe.io/v1/states'
            api = company.nfe_api
            if not api:
                raise osv.except_osv('Error','Please provide  valid API')
            headers = {'content-type': 'application/json','Authorization':'Basic %s'%api}
            r = requests.get(url, headers=headers)
            result = r.json()
            if isinstance(result,list):
                raise osv.except_osv('Congratulations',' API Test Successful')
            else:
                raise osv.except_osv('Invalid API'," To get API key please create account on http://app.nfe.io then go to 'Conta' tab , copy one of Nota Fiscal or Dados key and paste in 'NFEIO API' text box and validate") 
            
    def address_dict(self, cr, uid, zip, company_id,  context=None):
        if not zip:
            raise osv.except_osv('Error','Please provide  valid ZIP')
        if company_id:
            api = self.pool.get('res.company').browse(cr, uid, company_id).nfe_api
            if not api:
                raise osv.except_osv('Error','Please provide  valid API')
        else:
            raise osv.except_osv('Error','Please define a company')
        
        city_obj = self.pool.get('l10n_br_base.city')
        state_obj = self.pool.get('res.country.state')
        country_obj = self.pool.get('res.country')
        
        url = 'http://open.nfe.io/v1/addresses/'+ zip  
        headers = {'content-type': 'application/json','Authorization':'Basic %s'%api}
        r = requests.get(url, headers=headers)
        result = r.json()
        if 'message' in result.keys() and result['message'] =='Authorization has been denied for this request.':
                raise osv.except_osv('Error','Please provide correct API')  
        try:
            city_code = result['city']['code'][2:]
            state_code = result['state']['code']
            district = result['district']
            street = result['street']
            suffix = result['streetSuffix']
            country_ids = country_obj.search(cr, uid, [('code','=','BR')])
            state_ids = state_obj.search(cr, uid, [('ibge_code','=', state_code)])
            city_ids = city_obj.search(cr, uid, [('ibge_code','=',city_code)])
            
            address_dict = {
                            'country_id':country_ids and country_ids[0],
                            'state_id':state_ids and state_ids[0],
                            'l10n_br_city_id':city_ids and city_ids[0],
                            'district':district,
                            'street':suffix +' ' +street,
                            'is_nfeio':True
                            }
            return address_dict
        except:
            raise osv.except_osv('Warning','Address not found')
        
        
    def client_dict(self, cr, uid, cnpj, company_id,  context=None):
        if not cnpj:
            raise osv.except_osv('Error','Please provide  valid CNPJ')
        if not company_id:
            company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        if company_id:
            api = self.pool.get('res.company').browse(cr, uid, company_id).nfe_api
            if not api:
                raise osv.except_osv('Error','Please provide  valid API')
        else:
            raise osv.except_osv('Error','Please define a company')
        
        city_obj = self.pool.get('l10n_br_base.city')
        state_obj = self.pool.get('res.country.state')
        country_obj = self.pool.get('res.country')
        cnae_obj = self.pool.get('l10n_br_account.cnae')
        
        # remove all special characters from cnpj
        cnpj = ''.join(e for e in cnpj if e.isalnum())
        url = 'http://open.nfe.io/v1/legalpersons/'+ cnpj  
        headers = {'content-type': 'application/json','Authorization':'Basic %s'%api}
        r = requests.get(url, headers=headers)
        try:
            result = r.json() 
            print "result...............",result
    
            if 'message' in result.keys() and  'Not Found for CNPJ number' in result['message']:
                    raise osv.except_osv('Error','CNPJ Not Found') 
        
            city_code = str(result['endereco']['cidade']['codigo'])[2:] 
            state_code = result['endereco']['estado']
            district = result['endereco']['bairro']
            street = result['endereco']['logradouro']
            number = result['endereco']['numero']
            zip = result['endereco']['cep']
            legal_name = result['razaoSocial'],
            name = result['nomeFantasia']
            street2 = result['endereco']['complemento'],
            
            country_ids = country_obj.search(cr, uid, [('code','=','BR')])
            state_ids = state_obj.search(cr, uid, [('code','=',state_code)])
            city_ids = city_obj.search(cr, uid, [('ibge_code','=',city_code)])
            
            atividadePrincipal = result['atividadePrincipal']
            atividadesSecundarias = result['atividadesSecundarias']
            
            regimeTributario = result['regimeTributario']
            situacaoCadastral = result['situacaoCadastral']
            naturezaJuridica  = result['naturezaJuridica']
            dataSituacaoCadastral = result['dataSituacaoCadastral'] and  result['dataSituacaoCadastral'].replace('T',' ') or False
            dataCadastroMei = result['dataCadastroMei'] and result['dataCadastroMei'].replace('T',' ') or False
            dataAbertura = result['dataAbertura'] and result['dataAbertura'].replace('T',' ') or False
            
    
            cnae_ids = []
            if atividadePrincipal:
                cnae = atividadePrincipal.rsplit('-',1)
                cnae_code = cnae[0]
                cnae_name = cnae[1]
                cnae_ids = cnae_obj.search(cr, uid, [('code','=',cnae_code)])
                if not len(cnae_ids):
                    cnae_ids = [cnae_obj.create(cr, uid, {'code':cnae_code, 'name':cnae_name, 'version':1.0, 'internal_type':'normal'})]
            
            # compute secondary cnae
            secondary_cnae_ids = []
            if atividadesSecundarias:
                for secondary_cnae in atividadesSecundarias:
                    scnae = secondary_cnae.rsplit('-',1)
                    scnae_code = scnae[0]
                    scnae_name = scnae[1].strip()
                    scane_ids = cnae_obj.search(cr, uid, [('code','=',scnae_code)])
                    if not len(scane_ids):
                        scnae_ids = [cnae_obj.create(cr, uid, {'code':scnae_code, 'name':scnae_name, 'version':1.0, 'internal_type':'normal'})]
                        secondary_cnae_ids.append(scnae_ids[0])
                    else:
                        secondary_cnae_ids.append(scane_ids[0])
                secondary_cnae_ids = list(set(secondary_cnae_ids))  

            client_dict = {	
    					   	'name':name,
    					    'legal_name':legal_name and legal_name[0],
                            'country_id':country_ids and country_ids[0],
                            'state_id':state_ids and state_ids[0],
                            'l10n_br_city_id':city_ids and city_ids[0],
                            'district':district,
                            'street':street,
                            'street2':street2 and street2[0],
                            'number':number,
                            'zip':zip,
                            'cnae_main_id':cnae_ids and cnae_ids[0],
                            'cnae_secondary_ids':[(6,0,secondary_cnae_ids)],
                            'fiscal_type':regimeTributario,
                            'situacaoCadastral':situacaoCadastral,
                            'naturezaJuridica':naturezaJuridica,
                            'dataSituacaoCadastral':dataSituacaoCadastral,
                            'dataCadastroMei':dataCadastroMei,
                            'dataAbertura':dataAbertura,
                            'is_nfeio':True,
                            'is_company':True,
                            'nfeio_fetch_date':datetime.now(),
                            }
              
            return client_dict
        except:
            raise osv.except_osv('Warning','CNPJ not found')
     
               

    def zip_search(self, cr, uid, ids, context=None):
        for company in self.browse(cr, uid, ids):
            zip = company.zip
            address_dict = self.address_dict(cr, uid, zip, company.id, context=context)
            self.write(cr, uid, ids, address_dict, context=context)
        return True
    
    
    def cnpj_search(self, cr, uid, ids, context=None):
        for company in self.browse(cr, uid, ids):
            cnpj = company.cnpj_cpf
            client_dict = self.client_dict(cr, uid, cnpj, company.id, context=context)
            self.write(cr, uid, ids, client_dict, context=context)
        return True
            