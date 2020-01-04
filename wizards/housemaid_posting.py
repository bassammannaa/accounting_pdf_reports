# -*- coding: utf-8 -*-
###############################################################################
# Create new folder called wizard
# add python file __init__.py
# add file name to file __init__.py
# make sure

###############################################################################
from odoo import models, fields, api


class HousemaidPosting(models.TransientModel):
    _name = "account.report.housemaidposting"
    _description = "Housemaid Posting"

    from_date = fields.Date(string="Transactions From Date")
    to_date = fields.Date(string="Transactions To Date")
    selected_account = fields.Many2one(comodel_name="account.account", string="Account",
                                       required=True, )
    posting_type = fields.Selection(string="Posting Type",
                                    selection=[('dr_cr', 'DR\CR'), ('dr', 'DR'), ('cr', 'CR'), ],
                                    required=False, default='dr_cr')
    link_to_application = fields.Boolean(string="Link To Application", default=True, )
    application_comparison = fields.Boolean(string="Application Comparison", default=False, )

    @api.multi
    def print_report(self):
        data = {}
        data['from_date'] = self.from_date
        data['to_date'] = self.to_date
        data['selected_account'] = self.selected_account.id
        data['posting_type'] = self.posting_type
        data['link_to_application'] = self.link_to_application
        data['application_comparison'] = self.application_comparison



        report = self.env.ref('accounting_pdf_reports.housemaidposting_action')
        return report.report_action(self, data=data)