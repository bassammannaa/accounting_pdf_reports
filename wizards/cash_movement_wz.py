# -*- coding: utf-8 -*-
###############################################################################
# Create new folder called wizard
# add python file __init__.py
# add file name to file __init__.py
# make sure

###############################################################################
from odoo import models, fields, api


class CashMovement(models.TransientModel):
    _name = "account.report.cash_movement"
    _description = "Cash Movement"

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    journal_ids = fields.Many2one('account.journal', string='Cash Journals', required=False, domain=[('type','in', ['cash', 'bank'])])
    report_generation = fields.Selection(string="Report Generation", selection=[('pdf', 'PDF'), ('excel', 'Excel'), ],
                                         default='excel', required=False, )


    @api.multi
    def print_report(self):
        data = {}
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        data['report_generation'] = self.report_generation
        data['journal_ids'] = self.journal_ids.id

        if self.report_generation == 'pdf':
            report = self.env.ref('accounting_pdf_reports.cash_movement_action')
        else:
            report = self.env.ref('accounting_pdf_reports.cash_movement_action_excel')
        return report.report_action(self, data=data)
