# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountReportGeneralLedger(models.TransientModel):
    _inherit = "account.common.account.report"
    _name = "account.report.general.ledger"
    _description = "General Ledger Report"

    initial_balance = fields.Boolean(string='Include Initial Balances',
                                    help='If you selected date, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you\'ve set.')
    sortby = fields.Selection([('sort_date', 'Date'), ('sort_journal_partner', 'Journal & Partner')], string='Sort by', required=True, default='sort_date')
    journal_ids = fields.Many2many('account.journal', 'account_report_general_ledger_journal_rel', 'account_id', 'journal_id', string='Journals', required=True)
    selected_account = fields.Many2one(comodel_name="account.account", string="Account",
                                      required=False,)




    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])
        data['form'].update({'selected_account': self.selected_account.id if self.selected_account else 0})

        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        records = self.env[data['model']].browse(data.get('ids', []))

        return self.env.ref('accounting_pdf_reports.action_report_general_ledger').\
            with_context(landscape=True).report_action(records, data=data)
