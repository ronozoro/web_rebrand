# -*- coding: utf-8 -*-
{
    'name': 'Web User ReBrand',
    'category': 'Branding',
    'author': 'Mostafa Mohamed',
    'website': 'https://eg.linkedin.com/in/mostafa-mohammed-449a8786',
    'price': 10.00,
    'currency': 'EUR',
    'version': '1.0.1',
    'depends': ['base', 'web', 'web_widget_color'],
    'data': ['views/res_theme_view.xml',
             'views/res_users_view.xml',
             'views/web_user_rebrand.xml',
             'data/res_theme_data.xml',
             ],
    'js': ['static/src/js/web_theme.js'],
    'css': [],
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
    'installable': True
}
