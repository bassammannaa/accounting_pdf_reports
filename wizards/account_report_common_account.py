# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountCommonAccountReport(models.TransientModel):
    _name = 'account.common.account.report'
    _description = 'Account Common Account Report'
    _inherit = "account.common.report"

    display_account = fields.Selection([('all', 'All'), ('movement', 'With movements'),
                                        ('not_zero', 'With balance is not equal to 0'), ],
                                       string='Display Accounts', required=True, default='movement')
    group_by_type = fields.Selection(string="Group By Type", selection=[('yes', 'Yes'), ('no', 'No'), ], default='no', )

    @api.multi
    def pre_print_report(self, data):
        data['form'].update(self.read(['display_account'])[0])
        data['form'].update(self.read(['group_by_type'])[0])
        return data
