from contextlib import nullcontext
import json
from os import environ
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError
from odoo.exceptions import except_orm

class MyAPIController(http.Controller):
    
    
    @http.route('/confirm',type='json', auth='user', methods=['POST'],csrf=False )
    def transfer_stock(self,**kw):
        
     try:
         print("Entra operacion de confirmar")
         
         
          # Verificar si el usuario tiene permisos
         if not request.env.user.user_has_groups('stock.group_stock_manager'):
          raise AccessError("No tienes los permisos necesarios para realizar esta acción.")

         ref = request.params.get("name")  # Obtener el valor del parámetro "name"

         print(f"Ref: {request.params}")

         # Obtener los registros de ubicaciones y productos
         domain = [('name', '=', ref)]
         picking = request.env['stock.picking'].search(domain)
                 # Obtener los datos necesarios de la solicitud
         backorder_picking = False  
         for move in picking.move_lines:
            if move.product_uom_qty > move.quantity_done and move.quantity_done != 0:
            
             # Crear un nuevo traslado (backorder) con la diferencia de cantidades
             backorder_picking = True
             break
         # Verificar si hay cantidades hechas en el traslado
         if not any(move.quantity_done > 0 for move in picking.move_lines):
            raise UserError("Aún no ha registrado las cantidades hechas")
 
         
         
         print(f"Ref: {backorder_picking}")
         # Obtener los datos necesarios de la solicitud
         confirmation = request.env['stock.backorder.confirmation'].with_context(button_validate_picking_ids=picking.id).create({})
         confirmation_id = confirmation.id
 
         confirmation_line = request.env['stock.backorder.confirmation.line'].with_context(button_validate_picking_ids=picking.id).create({
            'backorder_confirmation_id': confirmation_id,  # ID de la confirmación principal
            'picking_id': picking.id,  # ID de la transferencia
            'to_backorder': True  # Valor para el campo 'to_backorder'
         })
         confirmation_line_id = confirmation_line.id
 
         
         # Verificar si el usuario tiene permisos
         if not request.env.user.user_has_groups('stock.group_stock_manager'):
             return {
                 'success': False,
                 'message': 'No tienes los permisos necesarios para realizar esta acción.',
             }
 
         # Obtener el registro de la confirmación
         backorder_confirmation = request.env['stock.backorder.confirmation'].with_context(button_validate_picking_ids=picking.id).browse(confirmation_line_id)
 
 
         # Procesar la confirmación
         backorder_confirmation.process()
      
         
        

         data = {
            'success': True,
            'message': 'Traslado realizado con éxito.',
            'error': picking.id,
          }
         response_json = json.dumps(data, default=str) 
         return response_json
     except UserError as error:
        # Manejar excepciones UserError y retornar una respuesta de error con código de estado 400
         data = {
            'success': False,
            'message': 'Ocurrió un error durante el traslado.',
            'error' : str(error)
         }
         response_json = json.dumps(data, default=str) 
         return response_json
     
     except Exception as error:
         data = {
            'success': False,
            'message': 'Ocurrió un error durante el traslado.',
            'error' : str(error)
         }
         response_json = json.dumps(data, default=str) 
         return response_json







    
    @http.route('/updateProduct',type='json', auth='user', methods=['POST'],csrf=False )
    def upodate_move_ptoduct(self,**kw):
         print(f"ya entró")
         

         ref = request.params.get("name")  # Obtener el valor del parámetro "name"
         product_id = request.params.get("product_id") 
         quantity = request.params.get("quantity") 
         
         
         print(f"Ref: {request.params}")

          # Obtener los registros de ubicaciones y productos
         domain = [
             ('name', '=', ref),
             ('product_id', '=', product_id)
         ]
         picking = request.env['stock.picking'].search(domain)

        

         move_lines = []
        
         for move in picking.move_lines:
             print(f"FOR : {move.product_uom_qty} y el otro valor es {move.quantity_done}")
            
             if int(move.product_id) == int(product_id):
                 print("Entra")
                 # Agregar la línea de movimiento al nuevo traslado (backorder)
                 move_lines.append((1, move.id, {
                     'quantity_done': quantity
                     }
                     ))


         picking.write({'move_lines': move_lines})


       

         return {
             'success': True,
             'message': 'Cantidad Actualizada',
             'picking_id': picking.id,
         }
    @http.route('/getPicking',type='json', auth='user', methods=['POST'],csrf=False )
    def getPicking(self,**kw):
        
         
        picking_id = request.params.get("picking_id")  # Obtener el valor del parámetro "picking_id"
        domain = [('name', '=', picking_id)]

        picking = request.env['stock.picking'].search(domain)
        print(f"ya entró {picking}")
        products = []
        if picking.move_lines:
            products = picking.move_lines.mapped(lambda move: {
                'id': move.product_id.id,
                'barcode': move.product_id.barcode,
                'name': move.product_id.name,
                'um': move.product_id.uom_id.name,
                'demand': move.product_uom_qty,
                'image_url': move.product_id.product_tmpl_id.image_1920,
            })
            
        reception_data = {
            'success': True,
            'message': 'Operación exitosa',
            'error' : "no",
            'data' : products
         }
        
        response_json = json.dumps(reception_data, default=str)

        return response_json
    
    @http.route('/get_receptions', type='json', auth='user', methods=['POST'],csrf=False )
    def get_receptions(self,**kw):

     try:
        if not request.env.user.user_has_groups('stock.group_stock_manager'):
          raise AccessError("No tienes los permisos necesarios para realizar esta acción.")
        
        order_name = request.params.get("order")  # Obtener el valor del parámetro "name"
       
       
        
        # Obtener las recepciones relacionadas con la Orden de Compra
        
        receptions = request.env['stock.picking'].sudo().search(['|', ('origin', '=', order_name), ('name', '=', order_name)],
                                                                order='state, name desc')

        # Obtener los campos requeridos de las recepciones
        reception_data = []
        for reception in receptions:
            data = {
                'name': reception.name,
                'partner': reception.partner_id.name,
                'status': reception.state,
                'origin': reception.origin,
                'destination': reception.location_dest_id.complete_name,
            }

            reception_data.append(data)

        data_json = json.dumps(reception_data, default=str) 
        data2 = {
            'success': True,
            'message': 'Ocurrió un error durante el traslado.',
            'error' : "no",
            'data' : data_json
         }

        
        
        response_json = json.dumps(data2, default=str) 
        return response_json
     except UserError as error:
        # Manejar excepciones UserError y retornar una respuesta de error con código de estado 400
         data = {
            'success': False,
            'message': 'Ocurrió un error durante el traslado.',
            'error' : str(error)
         }
         response_json = json.dumps(data, default=str) 
         return response_json
     
     except Exception as error:
         data = {
            'success': False,
            'message': 'Ocurrió un error durante el traslado.',
            'error' : str(error)
         }
         response_json = json.dumps(data, default=str) 
         return response_json
