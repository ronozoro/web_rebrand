# -*- encoding: utf-8 -*-
{
    'name': "Backend Widget Color",
    'category': "web",
    'version': "9.0.1.0.0",
    "author": "Mostafa Mohamed",
    'website': 'https://eg.linkedin.com/in/mostafa-mohammed-449a8786',
    'depends': ['base', 'web'],
    'data': [
        'view/backend_widget_color_link.xml'
    ],
    'qweb': [
        'static/src/xml/widget.xml',
    ],
    'auto_install': False,
    'installable': True,
    'web_preload': True,
}
