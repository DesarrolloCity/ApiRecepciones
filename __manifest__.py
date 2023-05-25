# -*- coding: utf-8 -*-

{
    
    'name': 'Etiquetas con precio Makro',
    'version': '0.1',
    'author': 'Daniel Almaguer',
    'website': 'https://mx.linkedin.com/in/daniel-almaguer-valdez-b0768b215?original_referer=https%3A%2F%2Fwww.google.com%2F',
    'category': 'Labels',
    'summary': 'Desarrollo de etiquetas de precio para makro',
    'description': """

    """,
    'depends': ['base','product'],

    'data': [
               
              
                # Permisos de Acceso #
                'security/ir.model.access.csv',
                # Reportes #
                'reports/product_template_templates.xml',
                'reports/product_reports.xml',
                

            ],

    'demo': [

    ],
    'installable': True,
    'auto_install': False,
    'assets': {
    },
    'license': 'LGPL-3',
}
