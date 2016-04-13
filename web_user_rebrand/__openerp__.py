# -*- coding: utf-8 -*-
{
    'name': 'Web User ReBrand',
    'category': 'web',
    'description': """
        Customize backend color themes
    """,
    'author': 'Mostafa Mohamed',
    'website': 'https://eg.linkedin.com/in/mostafa-mohammed-449a8786',
    'version': '1.1',
    'depends': ['base', 'web', 'web_widget_color'],
    'data': ['views/res_theme_view.xml',
             'views/res_users_view.xml',
             'views/web_user_rebrand.xml',
             'data/res_theme_data.xml',
             ],
    'js': ['static/src/js/web_theme.js'],
    'css': [],
    'auto_install': False,
    'web_preload': False,
}
