{
    'name': 'Invoice Meter Reading',
    'version': '1.1.0',
    'category': 'Accounting',
    'summary': 'Add meter reading columns to invoices with replacement support',
    'depends': ['account', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/account_move_views.xml',
        'report/invoice_report_templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}