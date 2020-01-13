# -*- coding: utf-8 -*-

from odoo import models, api
import logging
from odoo.exceptions import ValidationError


logger = logging.getLogger(__name__)


class ReportAccountBalances(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_accounts_balances'
    _description = "Accounts Balances"


    def get_detailed_data(self):
        try:
            summary_data_list = []

            sql = ("""select 
                     b.id,
                     b.name,
                     d.name,
                     d.id,
                     d.rounding,
                     case when COALESCE(c.currency_id,0) != 96 then SUM(COALESCE(a.amount_currency, 0.0)) else SUM(COALESCE(a.debit, 0.0)) end,
                     case when COALESCE(c.currency_id,0) != 96 then SUM(COALESCE(a.amount_currency, 0.0)) else SUM(COALESCE(a.credit, 0.0)) end,
                     case when COALESCE(c.currency_id,0) != 96 then SUM(COALESCE(a.amount_currency, 0.0)) else SUM(COALESCE(a.debit, 0.0)) end -
                     case when COALESCE(c.currency_id,0) != 96 then SUM(COALESCE(a.amount_currency, 0.0)) else SUM(COALESCE(a.credit, 0.0)) end
                 from 
                     account_move_line a, 
                     account_account_type b,
                     account_account c,
                     res_currency d
                 where 
                     c.user_type_id=b.id
                     and a.account_id = c.id
                     and c.currency_id = d.id
                 group by 
                     b.id, b.name, c.currency_id,d.name,d.id,d.rounding
                 order by
                     b.id""")

            self.env.cr.execute(sql)
            for row in self.env.cr.fetchall():
                res = {
                    'application_id': row[0] if row[0] else 0.0,
                    'code': row[1] if row[1] else '',
                    'name': row[2] if row[2] else '',
                }
                summary_data_list.append(res)

            return summary_data_list
        except Exception as e:
            logger.exception("get_detailed_data Method")
            raise ValidationError(e)

    def summary_data(self):
        try:
            summary_data_list = []

            sql =("""select 
                    b.id,
                    b.name,
                    d.name,
                    d.id,
                    d.rounding,
                    case when COALESCE(c.currency_id,0) != 96 then SUM(COALESCE(a.amount_currency, 0.0)) else SUM(COALESCE(a.debit, 0.0)) end,
                    case when COALESCE(c.currency_id,0) != 96 then SUM(COALESCE(a.amount_currency, 0.0)) else SUM(COALESCE(a.credit, 0.0)) end,
                    case when COALESCE(c.currency_id,0) != 96 then SUM(COALESCE(a.amount_currency, 0.0)) else SUM(COALESCE(a.debit, 0.0)) end -
                    case when COALESCE(c.currency_id,0) != 96 then SUM(COALESCE(a.amount_currency, 0.0)) else SUM(COALESCE(a.credit, 0.0)) end
                from 
                    account_move_line a, 
                    account_account_type b,
                    account_account c,
                    res_currency d,
                    account_move e
                where 
                    c.user_type_id=b.id
                    and a.account_id = c.id
                    and c.currency_id = d.id
                    and e.id=a.move_id
                    and e.state ='posted'
                group by 
                    b.id, b.name, c.currency_id,d.name,d.id,d.rounding
                order by
                    b.id""")

            self.env.cr.execute(sql)
            for row in self.env.cr.fetchall():
                res = {
                    'account_type_id': row[0] if row[0] else 0.0,
                    'account_type': row[1] if row[1] else '',
                    'currency_name': row[2] if row[2] else '',
                    'currency_id': row[3] if row[3] else 0.0,
                    'rounding': row[4] if row[4] else 0.0,
                    'tot_debit': row[5] if row[5] else 0.0,
                    'tot_credit': row[6] if row[6] else 0.0,
                    'balance': row[7] if row[7] else 0.0,
                }
                summary_data_list.append(res)

            return summary_data_list
        except Exception as e:
            logger.exception("summary_data Method")
            raise ValidationError(e)

    @api.model
    def _get_report_values(self, docids, data=None):
        try:
            docargs = []
            domain = []
            report_title = ''

            docs = self.summary_data()


            # report_title = "(From Date: " + data['from_date'] + " To Date: " + data['to_date'] + ")"

            docargs = {
                'doc_ids': docids,
                'doc_model': 'account.move.line',
                'docs': docs,
                'title': report_title,
                'trans': self.get_detailed_data,
            }
            return docargs
        except Exception as e:
            logger.exception("Get Report Values Method")
            raise ValidationError(e)