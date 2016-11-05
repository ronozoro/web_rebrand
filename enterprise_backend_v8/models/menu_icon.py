from openerp import tools, api
import base64
import re
import operator
import logging
import openerp
from openerp.tools import convert
from openerp.addons.base.ir.ir_ui_menu import ir_ui_menu

original_xml_import = convert.xml_import

_logger = logging.getLogger(__name__)
escape_re = re.compile(r'(?<!\\)/')


def escape(x):
    return x.replace('\\/', '/')


class Menu(ir_ui_menu):
    # web_icon_data = openerp.fields.Binary(string='Web Icon Image',
    #                                       compute="_get_image_icon", store=True, attachment=True)
    #
    # @api.one
    # @api.depends('web_icon')
    # def _get_image_icon(self):
    #     print 'Called'
    #     for menu in self:
    #         menu.web_icon_data = self.read_image(menu.web_icon)

    @api.cr_uid_context
    @tools.ormcache_context(accepted_keys=('lang',))
    def load_menus_root(self, cr, uid, context=None):
        fields = ['name', 'sequence', 'parent_id', 'action', 'web_icon']
        menu_root_ids = self.get_user_roots(cr, uid, context=context)
        menu_roots = self.read(cr, uid, menu_root_ids, fields, context=context) if menu_root_ids else []
        return {
            'id': False,
            'name': 'root',
            'parent_id': [-1, ''],
            'children': menu_roots,
            'all_menu_ids': menu_root_ids,
        }

    @api.cr_uid_context
    @tools.ormcache_context(accepted_keys=('lang',))
    def load_menus(self, cr, uid, context=None):
        """ Loads all menu items (all applications and their sub-menus).

        :return: the menu root
        :rtype: dict('children': menu_nodes)
        """
        fields = ['name', 'sequence', 'parent_id', 'action', 'web_icon']
        menu_root_ids = self.get_user_roots(cr, uid, context=context)
        menu_roots = self.read(cr, uid, menu_root_ids, fields, context=context) if menu_root_ids else []
        print menu_roots
        menu_root = {
            'id': False,
            'name': 'root',
            'parent_id': [-1, ''],
            'children': menu_roots,
            'all_menu_ids': menu_root_ids,
        }
        if not menu_roots:
            return menu_root

        # menus are loaded fully unlike a regular tree view, cause there are a
        # limited number of items (752 when all 6.1 addons are installed)
        menu_ids = self.search(cr, uid, [('id', 'child_of', menu_root_ids)], 0, False, False, context=context)
        menu_items = self.read(cr, uid, menu_ids, fields, context=context)
        # adds roots at the end of the sequence, so that they will overwrite
        # equivalent menu items from full menu read when put into id:item
        # mapping, resulting in children being correctly set on the roots.
        menu_items.extend(menu_roots)
        menu_root['all_menu_ids'] = menu_ids  # includes menu_root_ids!

        # make a tree using parent_id
        menu_items_map = dict(
            (menu_item["id"], menu_item) for menu_item in menu_items)
        for menu_item in menu_items:
            if menu_item['parent_id']:
                parent = menu_item['parent_id'][0]
            else:
                parent = False
            if parent in menu_items_map:
                menu_items_map[parent].setdefault(
                    'children', []).append(menu_item)

        # sort by sequence a tree using parent_id
        for menu_item in menu_items:
            menu_item.setdefault('children', []).sort(
                key=operator.itemgetter('sequence'))

        return menu_root

    def read_image(self, path):
        if not path:
            return False
        icon_path = openerp.modules.get_module_resource(path)
        icon_image = False
        if icon_path:
            try:
                icon_file = tools.file_open(icon_path, 'rb')
                icon_image = base64.encodestring(icon_file.read())
            finally:
                icon_file.close()
        return icon_image


Menu()


class MenuXMLImport(original_xml_import):
    def _tag_menuitem(self, cr, rec, data_node=None, mode=None):
        menu_id = super(MenuXMLImport, self)._tag_menuitem(cr, rec, data_node=data_node, mode=mode)
        rec_id = rec.get("id", '').encode('ascii')
        self._test_xml_id(rec_id)
        m_l = map(escape, escape_re.split(rec.get("name", '').encode('utf8')))

        values = {'parent_id': False}
        if rec.get('parent', False) is False and len(m_l) > 1:
            # No parent attribute specified and the menu name has several menu components,
            # try to determine the ID of the parent according to menu path
            pid = False
            res = None
            values['name'] = m_l[-1]
            m_l = m_l[:-1]  # last part is our name, not a parent
            for idx, menu_elem in enumerate(m_l):
                if pid:
                    cr.execute('select id from ir_ui_menu where parent_id=%s and name=%s', (pid, menu_elem))
                else:
                    cr.execute('select id from ir_ui_menu where parent_id is null and name=%s', (menu_elem,))
                res = cr.fetchone()
                if res:
                    pid = res[0]
                else:
                    # the menuitem does't exist but we are in branch (not a leaf)
                    _logger.warning('Warning no ID for submenu %s of menu %s !', menu_elem, str(m_l))
                    pid = self.pool['ir.ui.menu'].create(cr, self.uid, {'parent_id': pid, 'name': menu_elem})
            values['parent_id'] = pid
        else:
            # The parent attribute was specified, if non-empty determine its ID, otherwise
            # explicitly make a top-level menu
            if rec.get('parent'):
                menu_parent_id = self.id_get(cr, rec.get('parent', ''))
            else:
                # we get here with <menuitem parent="">, explicit clear of parent, or
                # if no parent attribute at all but menu name is not a menu path
                menu_parent_id = False
            values = {'parent_id': menu_parent_id}
            if rec.get('name'):
                values['name'] = rec.get('name')
            try:
                res = [self.id_get(cr, rec.get('id', ''))]
            except:
                res = None

        if rec.get('action'):
            a_action = rec.get('action', '').encode('utf8')

            # determine the type of action
            action_type, action_id = self.model_id_get(cr, a_action)
            action_type = action_type.split('.')[-1]  # keep only type part

            if not values.get('name') and action_type in ('act_window', 'wizard', 'url', 'client', 'server'):
                a_table = 'ir_act_%s' % action_type.replace('act_', '')
                cr.execute('select name from "%s" where id=%%s' % a_table, (int(action_id),))
                resw = cr.fetchone()
                if resw:
                    values['name'] = resw[0]

        if not values.get('name'):
            # ensure menu has a name
            values['name'] = rec_id or '?'

        if rec.get('sequence'):
            values['sequence'] = int(rec.get('sequence'))

        if rec.get('groups'):
            g_names = rec.get('groups', '').split(',')
            groups_value = []
            for group in g_names:
                if group.startswith('-'):
                    group_id = self.id_get(cr, group[1:])
                    groups_value.append((3, group_id))
                else:
                    group_id = self.id_get(cr, group)
                    groups_value.append((4, group_id))
            values['groups_id'] = groups_value
        try:
            if not values.get('parent_id'):
                values['web_icon'] = openerp.modules.module.get_module_icon(self.module)
        except:
            pass
        pid = self.pool['ir.model.data']._update(cr, self.uid, 'ir.ui.menu', self.module, values, rec_id,
                                                 noupdate=self.isnoupdate(data_node), mode=self.mode,
                                                 res_id=res and res[0] or False)

        if rec_id and pid:
            self.idref[rec_id] = int(pid)

        if rec.get('action') and pid:
            action = "ir.actions.%s,%d" % (action_type, action_id)
            self.pool['ir.model.data'].ir_set(cr, self.uid, 'action', 'tree_but_open', 'Menuitem',
                                              [('ir.ui.menu', int(pid))], action, True, True, xml_id=rec_id)
        return menu_id


convert.xml_import = MenuXMLImport
