# -*- coding: utf-8 -*-
{
    'name': 'User Backend Branding',
    'category': 'Extra Tools',
    'author': 'Mostafa Mohamed',
    'website': 'https://eg.linkedin.com/in/mostafa-mohammed-449a8786',
    'price': 15.00,
    'currency': 'EUR',
    'version': '9.0.0.1',
    'depends': ['base', 'web', 'backend_widget_color'],
    'data': ['views/res_theme_view.xml',
             'views/res_users_view.xml',
             'views/web_user_rebrand.xml',
             'data/res_theme_data.xml',
             ],
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
    'installable': True
}
