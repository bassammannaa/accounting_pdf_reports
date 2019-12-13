# -*- coding: utf-8 -*-

from odoo import fields, models, _


class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.common.partner.report"
    _name = "account.report.partner.ledger"
    _description = "Account Partner Ledger"

    amount_currency = fields.Boolean("With Currency", default=True,
                                     help="It adds the currency column on report if the "
                                          "currency differs from the company currency.")
    reconciled = fields.Boolean('Reconciled Entries', default=False,)
    partner_sponsor = fields.Many2one(comodel_name="res.partner", string="Sponsor",
                                      required=False, domain=[('is_company','=', False)])
    partner_external_offfice = fields.Many2one(comodel_name="res.partner",
                                               string="External Office", required=False,
                                               domain=[('is_company','=', True)])
    selected_account = fields.Many2one(comodel_name="account.account", string="Account",
                                       required=False, )

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update(
            {'reconciled': self.reconciled,
             'amount_currency': self.amount_currency,
             'partner_sponsor': self.partner_sponsor.id,
             'partner_external_offfice': self.partner_external_offfice.id,
             'selected_account': self.selected_account.id if self.selected_account else 0,
             }
        )
        return self.env.ref('accounting_pdf_reports.action_report_partnerledger').report_action(self, data=data)
