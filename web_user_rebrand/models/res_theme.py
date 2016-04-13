# -*- encoding: utf-8 -*-
from openerp import fields, models, tools, api, _,http, SUPERUSER_ID
from openerp.osv import osv
import openerp
from openerp.addons.web.controllers.main import Binary
import functools
from openerp.http import request
from openerp.modules import get_module_resource
from cStringIO import StringIO
db_monodb = http.db_monodb
import re


class res_theme(models.Model):
    _name = "res.theme"
    _rec_name = 'name'

    name = fields.Char(string='Theme Name', required=True)
    users = fields.One2many('res.users', 'theme_id', string='Users')
    default_view = fields.Boolean(string='Default')
    # Top Corner
    top_bg_color = fields.Char(string='Background Color')
    top_border_color = fields.Char(string='Border Color')
    top_font_color = fields.Char(string='Font Color')
    top_active_font_color = fields.Char(string='Active Item Font Color')
    top_active_bg_color = fields.Char(string='Active Item Background Color')
    top_hover_font_color = fields.Char(string='Hover Font Color')
    top_hover_bg_color = fields.Char(string='Hove Background Color')
    # left corner
    left_bg_color = fields.Char(string='Background Color')
    left_main_menu_color = fields.Char(string='Main Menu Color')
    left_sub_menu_color = fields.Char(string='Sub Menu Color')
    left_active_font_color = fields.Char(string='Active Item Font Color')
    left_active_bg_color = fields.Char(string='Active Item Background Color')
    left_hover_font_color = fields.Char(string='Hover Font Color')
    left_hover_bg_color = fields.Char(string='Hover Background Color')
    # button
    button_font_color = fields.Char(string='Button Font Color')
    button_bg_color = fields.Char(string='Button Background Color X')
    button_bg_color_2 = fields.Char(string='Button Background Color Y')
    button_highlight_color = fields.Char(string='Button Highlight Color')
    button_highlight_font_color = fields.Char(string='Button Highlight font color')
    # header Section
    header_section_bg = fields.Char(string='Head Section Background Color')
    header_section_font_color = fields.Char(string='Head Section Font Color')
    # footer
    image_medium = fields.Binary(string='Favicon')
    footer_string = fields.Char(string='Replace Footer (Odoo) by')
    title_string = fields.Char(string='Replace Title (Odoo) by')
    url_string = fields.Char(string='(Odoo) HyberLink')
    odoo_color = fields.Char(string='(Odoo) Color')
    # hide Odoo Preferences items
    hide_prefe = fields.Boolean(string='Hide Preferences')
    hide_about = fields.Boolean(string='Hide Developer Mode (About)')
    hide_account = fields.Boolean(string='Hide Account')
    hide_help = fields.Boolean(string='Hide Help')

    @api.model
    def create(self, vals):
        res = super(res_theme, self).create(vals)
        new_ids = self.env['res.theme'].search([('default_view', '=', True)])
        if new_ids and vals['default_view'] == True:
            raise osv.except_osv(_('Error!'),
                                 _('Sorry only 1 default Theme is applied per database\n'
                                   'Please Recheck Default value'))
        else:
            return res

    def get_the_theme(self, cr, uid, ids, context=None):
        print ('Calllllled ?')
        print ('Calllllled ?')
        print ('Calllllled ?')
        users = self.pool.get('res.users')
        current_user = users.browse(cr, uid, uid, context=context)
        sasa = self.search_read(cr, SUPERUSER_ID, [('default_view', '=', True)], context=context)
        if current_user.theme_id:
            mostafa = self.search_read(cr, SUPERUSER_ID, [('id', '=', current_user.theme_id.id)], context=context)
            print('Here is the Data : ', mostafa)
            return mostafa
        elif sasa:
            print('Here is the Data : ', sasa)
            return sasa
        else:
            return False

    def get_the_fac_icon(self, cr, uid, ids, context=None):
        users = self.pool.get('res.users')
        current_user = users.browse(cr, uid, uid, context=context)
        sasa = self.search_read(cr, SUPERUSER_ID, [('default_view', '=', True)], context=context)[0]
        print ('sasa :',sasa['image_medium'])
        if current_user.theme_id:
            mostafa = self.search_read(cr, SUPERUSER_ID, [('id', '=', current_user.theme_id.id)], context=context)[0]
            return mostafa['image_medium']
        elif sasa:
            return sasa['image_medium']
        else:
            return False




res_theme()


class res_users_theme(models.Model):
    _inherit = 'res.users'

    theme_id = fields.Many2one('res.theme', string='Theme')


res_users_theme()


class ir_translation(models.Model):
    _inherit = 'ir.translation'

    def _debrand(self, cr, uid, source):
        users = self.pool.get('res.users')
        current_user = users.browse(cr, uid, uid)
        if not source or not re.search(r'\bodoo\b', source, re.IGNORECASE):
            return source

        new_name = current_user.theme_id.footer_string

        if not new_name:
            return source

        return re.sub(r'\bodoo\b', new_name, source, flags=re.IGNORECASE)

    @tools.ormcache(skiparg=3)
    def _get_source(self, cr, uid, name, types, lang, source=None, res_id=None):
        res = super(ir_translation, self)._get_source(cr, uid, name, types, lang, source, res_id)
        return self._debrand(cr, uid, res)


ir_translation()

class BinaryCustom(Binary):
    @http.route([
        '/web/binary/company_logo',
        '/logo',
        '/logo.png',
    ], type='http', auth="none")
    def company_logo(self, dbname=None, **kw):
        imgname = 'logo.png'
        default_logo_module = 'web_user_rebrand'
        if request.session.db:
            request.env['ir.config_parameter'].get_param('web_user_rebrand.default_logo_module')
        placeholder = functools.partial(get_module_resource, default_logo_module, 'static', 'src', 'img')
        uid = None
        if request.session.db:
            dbname = request.session.db
            uid = request.session.uid
        elif dbname is None:
            dbname = db_monodb()

        if not uid:
            uid = openerp.SUPERUSER_ID

        if not dbname:
            response = http.send_file(placeholder(imgname))
        else:
            try:
                registry = openerp.modules.registry.Registry(dbname)
                with registry.cursor() as cr:
                    cr.execute("""SELECT c.logo_web, c.write_date
                                    FROM res_users u
                               LEFT JOIN res_company c
                                      ON c.id = u.company_id
                                   WHERE u.id = %s
                               """, (uid,))
                    row = cr.fetchone()
                    if row and row[0]:
                        image_data = StringIO(str(row[0]).decode('base64'))
                        response = http.send_file(image_data, filename=imgname, mtime=row[1])
                    else:
                        response = http.send_file(placeholder('nologo.png'))
            except Exception:
                response = http.send_file(placeholder(imgname))

        return response

    # @http.route(["/web/static/src/img/favicon.ico"],type='http', auth="none")
    # def fav_ico(self, dbname=None, **kw):
    #     print 'Calllled 3 3'
    #     imgname = 'logo.png'
    #     default_logo_module = 'web_user_rebrand'
    #     print request
    #     if request.session.db:
    #         request.env['ir.config_parameter'].get_param('web_user_rebrand.default_logo_module')
    #     placeholder = functools.partial(get_module_resource, default_logo_module, 'static', 'src', 'img')
    #     uid = None
    #     if request.session.db:
    #         dbname = request.session.db
    #         uid = request.session.uid
    #     elif dbname is None:
    #         dbname = db_monodb()
    #
    #     if not uid:
    #         uid = openerp.SUPERUSER_ID
    #
    #     if not dbname:
    #         response = http.send_file(placeholder(imgname))
    #     else:
    #         try:
    #             registry = openerp.modules.registry.Registry(dbname)
    #             with registry.cursor() as cr:
    #                 cr.execute("""SELECT c.logo_web, c.write_date
    #                                 FROM res_users u
    #                            LEFT JOIN res_company c
    #                                   ON c.id = u.company_id
    #                                WHERE u.id = %s
    #                            """, (uid,))
    #                 row = cr.fetchone()
    #                 if row and row[0]:
    #                     image_data = StringIO(str(row[0]).decode('base64'))
    #                     response = http.send_file(image_data, filename=imgname, mtime=row[1])
    #                 else:
    #                     response = http.send_file(placeholder('nologo.png'))
    #         except Exception:
    #             response = http.send_file(placeholder(imgname))
    #
    #     return response


BinaryCustom()
