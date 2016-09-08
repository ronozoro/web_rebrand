# -*- coding: utf-8 -*-
{
    'name': 'Notification Bar',
    'category': 'Extra Tools',
    'author': 'Mostafa Mohamed',
    'website': 'https://eg.linkedin.com/in/mostafa-mohammed-449a8786',
    'price': 38.00,
    'currency': 'EUR',
    'version': '1.0.1',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/template.xml',
        'views/notification_bar_view.xml'
    ],
    'qweb': [
        'static/src/xml/notify_bar.xml',
    ],
    'auto_install': False,
    'installable': True
}
