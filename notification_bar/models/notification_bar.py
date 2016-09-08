# -*- coding: utf-8 -*-
'''
 * Created by mostafa.
'''

from openerp import fields, models, api
from datetime import datetime, date
import datetime as dt
import calendar


class notification_bar(models.Model):
    _name = 'notification.bar'
    _rec_name = 'name'
    name = fields.Char(string='Name', required=True)
    model_id = fields.Many2one(comodel_name='ir.model', string='Model')
    field_id = fields.Many2one(comodel_name='ir.model.fields', string='Date Match Field', required=True)
    display_options = fields.Selection(selection=[('per_user', 'Per User'), ('for_all_users', 'For All Users')],
                                       required=True)
    reminder_options = fields.Selection(
        selection=[('per_day', 'Day per Day'), ('x_days', 'Next x Days'), ('current_month', 'Current Month'),
                   ('next_month', 'Next Month'), ],
        required=True)
    num_of_days = fields.Integer(string='Days', default=0)
    from_today = fields.Boolean(string='From Today', default=False)
    user_field_id = fields.Many2one(comodel_name='ir.model.fields', string='User Field ID')
    display_fields = fields.Many2many(comodel_name='ir.model.fields', string='Display Fields')
    active = fields.Boolean(string='Active', default=True)

    @api.multi
    @api.onchange('model_id', 'display_options', 'num_of_days')
    def onchange_model_id(self):
        model_fields = self.env['ir.model.fields'].search([('model_id', '=', self.model_id.id)])
        date_fields = self.env['ir.model.fields'].search(
            [('model_id', '=', self.model_id.id), ('ttype', 'in', ('date', 'datetime'))])
        user_field = self.env['ir.model.fields'].search(
            [('model_id', '=', self.model_id.id), ('relation', '=', 'res.users')])

        return {'domain': {'field_id': [('id', 'in', date_fields._ids)],
                           'user_field_id': [('id', 'in', user_field._ids)],
                           'display_fields': [('id', 'in', model_fields._ids)],}}

    def split(self, arr, size):
        arrs = []
        while len(arr) > size:
            pice = arr[:size]
            arrs.append(pice)
            arr = arr[size:]
        arrs.append(arr)
        return arrs

    def get_dates_xdays(self, today_date, num, flag):
        list_of_dates = []
        if flag:
            for g in range(num):
                new_date = str(today_date + dt.timedelta(days=g))
                list_of_dates.append(new_date)
            return list_of_dates
        else:
            for g in range(num):
                new_date = str(today_date + dt.timedelta(days=g + 1))
                list_of_dates.append(new_date)
            return list_of_dates

    def get_dates_current_month(self, today_date, last_day_date):
        list_of_dates = []
        delta = last_day_date - today_date
        for i in range(delta.days + 1):
            list_of_dates.append(str(today_date + dt.timedelta(days=i)))
        return list_of_dates

    def get_first_day(self, dt, d_years=0, d_months=0):
        y, m = dt.year + d_years, dt.month + d_months
        a, m = divmod(m - 1, 12)
        return date(y + a, m + 1, 1)

    def get_last_day(self, dts):
        return self.get_first_day(dts, 0, 1) + dt.timedelta(-1)

    def next_month(self, date):
        return date + dt.timedelta(days=calendar.monthrange(date.year, date.month)[1])

    def get_dates_next_month(self, today_date):
        last_day_of_next_month = self.get_last_day(self.next_month(today_date))
        return self.get_dates_current_month(today_date, last_day_of_next_month)

    def get_dates_next_month_false(self, today_date):
        last_day_of_next_month = self.get_last_day(self.next_month(today_date))
        first_day_of_next_month = self.get_first_day(self.next_month(today_date))
        return self.get_dates_current_month(first_day_of_next_month, last_day_of_next_month)

    @api.multi
    def get_notifications(self):
        data = []
        for record in self.browse(self.search([('active', '=', True)])._ids):
            new_dic = dict()
            new_dic['col'] = []
            new_dic['name'] = ''
            new_dic['value'] = []
            new_dic['link'] = []
            if record.display_options == 'per_user' and record.active == True:
                if record.reminder_options == 'per_day':
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, '=', str(datetime.now().date())),
                         (record.user_field_id.name, '=', self._uid)])
                elif record.reminder_options == 'x_days' and record.from_today:
                    list_of_dates = self.get_dates_xdays(today_date=datetime.now().date(), num=(record.num_of_days + 1),
                                                         flag=True)
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, 'in', list_of_dates),
                         (record.user_field_id.name, '=', self._uid)])
                elif record.reminder_options == 'x_days' and not record.from_today:
                    list_of_dates = self.get_dates_xdays(today_date=datetime.now().date(), num=(record.num_of_days + 1),
                                                         flag=False)
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, 'in', list_of_dates),
                         (record.user_field_id.name, '=', self._uid)])
                elif record.reminder_options == 'current_month' and record.from_today:
                    list_of_dates = self.get_dates_current_month(today_date=datetime.now().date(),
                                                                 last_day_date=self.get_last_day(datetime.now().date()))
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, 'in', list_of_dates),
                         (record.user_field_id.name, '=', self._uid)])

                elif record.reminder_options == 'current_month' and not record.from_today:

                    list_of_dates = self.get_dates_current_month(today_date=self.get_first_day(datetime.now().date()),
                                                                 last_day_date=self.get_last_day(datetime.now().date()))
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, 'in', list_of_dates),
                         (record.user_field_id.name, '=', self._uid)])
                elif record.reminder_options == 'next_month' and record.from_today:
                    list_of_dates = self.get_dates_next_month(today_date=datetime.now().date())
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, 'in', list_of_dates),
                         (record.user_field_id.name, '=', self._uid)])

                elif record.reminder_options == 'next_month' and not record.from_today:
                    list_of_dates = self.get_dates_next_month_false(today_date=datetime.now().date())
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, 'in', list_of_dates),
                         (record.user_field_id.name, '=', self._uid)])
                else:
                    data_ids = []
                for link in data_ids:
                    new_dic['link'].append(
                        {'name': ("/web?#id=" + str(link.id) + '&view_type=form&model=' + str(record.model_id.model))})
                if data_ids:
                    new_dic['name'] = record.name

                    for field in record.display_fields:
                        new_dic['col'].append({'name': field.field_description})

                    for new in data_ids:
                        for fields in record.display_fields:
                            if fields.ttype in ['char', 'text', 'boolean', 'date', 'datetime', 'float', 'integer',
                                                'html', 'monetary']:

                                if new.mapped(fields.name)[0] == False:
                                    new_dic['value'].append({'name': ' ', 'link': (
                                        "/web?#id=" + str(new.id) + '&view_type=form&model=' + str(
                                            record.model_id.model))})
                                elif new.mapped(fields.name)[0] == 0.0:
                                    new_dic['value'].append({'name': new.mapped(fields.name)[0], 'link': (
                                        "/web?#id=" + str(new.id) + '&view_type=form&model=' + str(
                                            record.model_id.model))})
                                elif new.mapped(fields.name)[0] != None:
                                    new_dic['value'].append({'name': new.mapped(fields.name)[0], 'link': (
                                        "/web?#id=" + str(new.id) + '&view_type=form&model=' + str(
                                            record.model_id.model))})

                            elif fields.ttype == 'many2one':
                                if new.mapped(fields.name).name != False:
                                    new_dic['value'].append({'name': new.mapped(fields.name).name, 'link': (
                                        "/web?#id=" + str(new.id) + '&view_type=form&model=' + str(
                                            record.model_id.model))})
                            else:
                                new_dic['value'].append({'name': ' ', 'link': (
                                    "/web?#id=" + str(new.id) + '&view_type=form&model=' + str(record.model_id.model))})
                new_dic['value'] = self.split(new_dic['value'], len(record.display_fields._ids))
                if new_dic['name'] != '':
                    data.append(new_dic)
            elif record.display_options == 'for_all_users' and record.active == True:
                if record.reminder_options == 'per_day':
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, '=', str(datetime.now().date()))])
                elif record.reminder_options == 'x_days' and record.from_today:
                    list_of_dates = self.get_dates_xdays(today_date=datetime.now().date(), num=(record.num_of_days + 1),
                                                         flag=True)
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, 'in', list_of_dates)])
                elif record.reminder_options == 'x_days' and not record.from_today:
                    list_of_dates = self.get_dates_xdays(today_date=datetime.now().date(), num=(record.num_of_days + 1),
                                                         flag=False)
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, 'in', list_of_dates)])
                elif record.reminder_options == 'current_month' and record.from_today:
                    list_of_dates = self.get_dates_current_month(today_date=datetime.now().date(),
                                                                 last_day_date=self.get_last_day(datetime.now().date()))
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, 'in', list_of_dates)])
                elif record.reminder_options == 'current_month' and not record.from_today:
                    list_of_dates = self.get_dates_current_month(today_date=self.get_first_day(datetime.now().date()),
                                                                 last_day_date=self.get_last_day(datetime.now().date()))
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, 'in', list_of_dates)])


                elif record.reminder_options == 'next_month' and record.from_today:
                    list_of_dates = self.get_dates_next_month(today_date=datetime.now().date())
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, 'in', list_of_dates)])

                elif record.reminder_options == 'next_month' and not record.from_today:
                    list_of_dates = self.get_dates_next_month_false(today_date=datetime.now().date())
                    data_ids = self.env[record.model_id.model].search(
                        [(record.field_id.name, 'in', list_of_dates)])
                else:
                    data_ids = []

                for link in data_ids:
                    new_dic['link'].append(
                        {'name': ("/web?#id=" + str(link.id) + '&view_type=form&model=' + str(record.model_id.model))})
                if data_ids:
                    new_dic['name'] = record.name
                    for field in record.display_fields:
                        new_dic['col'].append({'name': field.field_description})
                    for new in data_ids:
                        for fields in record.display_fields:
                            if fields.ttype in ['char', 'text', 'boolean', 'date', 'datetime', 'float', 'integer',
                                                'html', 'monetary']:
                                if new.mapped(fields.name)[0] == False:
                                    new_dic['value'].append({'name': ' ', 'link': (
                                        "/web?#id=" + str(new.id) + '&view_type=form&model=' + str(
                                            record.model_id.model))})
                                elif new.mapped(fields.name)[0] == 0.0:
                                    new_dic['value'].append({'name': new.mapped(fields.name)[0], 'link': (
                                        "/web?#id=" + str(new.id) + '&view_type=form&model=' + str(
                                            record.model_id.model))})
                                elif new.mapped(fields.name)[0] != None:
                                    new_dic['value'].append({'name': new.mapped(fields.name)[0], 'link': (
                                        "/web?#id=" + str(new.id) + '&view_type=form&model=' + str(
                                            record.model_id.model))})

                            elif fields.ttype == 'many2one':
                                if new.mapped(fields.name).name != False:
                                    new_dic['value'].append({'name': new.mapped(fields.name).name, 'link': (
                                        "/web?#id=" + str(new.id) + '&view_type=form&model=' + str(
                                            record.model_id.model))})
                            else:
                                new_dic['value'].append({'name': ' ', 'link': (
                                    "/web?#id=" + str(new.id) + '&view_type=form&model=' + str(record.model_id.model))})
                new_dic['value'] = self.split(new_dic['value'], len(record.display_fields._ids))
                if new_dic['name'] != '':
                    data.append(new_dic)
        sums = 0
        for g in data:
            sums += len(g['link'])
        return [data, sums]


notification_bar()
