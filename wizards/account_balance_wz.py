# -*- coding: utf-8 -*-
###############################################################################
# Create new folder called wizard
# add python file __init__.py
# add file name to file __init__.py
# make sure

###############################################################################
from odoo import models, fields, api


class AccountBalanceWZ(models.TransientModel):
    _name = "account.report.account_balance_wz"
    _description = "Account Balance"

    as_of_date = fields.Date(string="As of Date")
    account_type = fields.Many2one(comodel_name="account.account.type", string="Account Type", required=False, )


    @api.multi
    def print_report(self):
        data = {}
        data['as_of_date'] = self.as_of_date if self.as_of_date else ''
        data['account_type'] = self.account_type.id if self.account_type else 0

        report = self.env.ref('accounting_pdf_reports.action_report_accounts_balances')
        return report.report_action(self, data=data)