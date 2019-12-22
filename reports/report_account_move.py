from datetime import datetime
import time

from odoo import models, api


class AccountMovementReport(models.AbstractModel):
    _name = "report.accounting_pdf_reports.report_account_move"
    _description = "Account Movement Report"

    def get_move_lines(self, docs):
        account_move_lines_obj = self.env['account.move.line'].search([('move_id', '=', docs.id)])
        # account_move_lines_obj = self.env['account.move.line'].search([('move_id', 'in', (6893,24221))])
        account_move_lines = []
        for account_move_line in account_move_lines_obj:
            res = {
                'account_code': account_move_line.account_id.code,
                'account_name': account_move_line.account_id.name,
                'partner_name': account_move_line.partner_id.name,
                'hm_name': account_move_line.application_id.external_office_id,
                'office_name': account_move_line.office_branch.name,
                'debit': account_move_line.debit,
                'credit': account_move_line.credit,
                'amount_currency': account_move_line.amount_currency if account_move_line.currency_id else abs(account_move_line.balance),
                'rate': (account_move_line.amount_currency / account_move_line.balance_cash_basis) if account_move_line.balance_cash_basis > 0 else 1 ,
                'currency_name': account_move_line.currency_id.name if account_move_line.currency_id else account_move_line.company_currency_id.name,
            }
            account_move_lines.append(res)
        return account_move_lines


    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)

        docargs = {
            'doc_model': 'account.move',
            'docs': docs,
            'account_move_lines': self.get_move_lines,
        }
        return docargs
