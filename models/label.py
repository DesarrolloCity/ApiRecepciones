
import decimal
from os import environ
from odoo import models, fields, api
from random import randint
from odoo.exceptions import UserError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
    
class Label(models.Model):
    _inherit = ['product.template']
 

class productLayout(models.TransientModel):
    _inherit = ['product.label.layout']
    
    product_ids = fields.Many2many('product.product')
    product_tmpl_ids = fields.Many2many('product.template')
     
   
    def get_product_price(self,id):
        current = fields.Datetime.now()
        current.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        product_price= {}
        #print("id : " + str(id))
        price_list_products_ids= self.env['product.pricelist.item'].search([
             '&',
             '|',
            ('date_end', '>=', current),
            ('date_end', '=', False),
            ('product_tmpl_id', 'in', [id])
         ],order='date_end,create_date desc')
        price_list_products_ids = sorted(price_list_products_ids, key=lambda x: x.min_quantity)

        count = len(price_list_products_ids)
        #print(f"Count:  {count}")

        return price_list_products_ids
          
    def get_product_price_with_tax(self,id,price):
        product = self.env['product.template'].browse(id)

        # Obtener los impuestos asociados al producto
        taxes = product.taxes_id 

        # Recorrer los impuestos y obtener la información relevante
        
        if len(taxes) > 1:
         for tax in taxes:
        
          tax_amount = tax.amount
         
          tax_product = ((tax_amount / 100)  *  price) + price
          #print(f"Impuesto2 : {(tax_amount / 100)}, Precio: { price }")
          #print(f"Impuesto: {tax_product}, Tasa: {round((tax_amount / 100),2)  *  price}")
                  
          return tax_product
        else:
          return price

    def view_labels_report(self):
               
        for item in self.product_tmpl_ids: 
            #print(f"Tipo : {(item.type)}")
            
            if (item.type == 'service'):
               raise UserError(str(item.name) + ' no es producto almacenable, favor de verificar' )
            
            if (len(item.taxes_id) < 1):
               raise UserError('El Producto '+ str(item.name) + ', no tiene impuestos favor verifique' )
            
            
          
        return self.env.ref('price_label_makro.report_product_template_label_makro').report_action(self)
    
    def get_current_company(self):
        user = self.env.user
        current_company = user.company_id
        return current_company.logo
