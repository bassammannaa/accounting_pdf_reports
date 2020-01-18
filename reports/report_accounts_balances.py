# -*- coding: utf-8 -*-

from odoo import models, api
import logging
from odoo.exceptions import ValidationError
from datetime import date, datetime
import datetime

logger = logging.getLogger(__name__)


class ReportAccountBalances(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_accounts_balances'
    _description = "Accounts Balances"

    def get_detailed_data(self, account_type_id, currency_id, as_of_date):
        try:
            summary_data_list = []

            sql = ("""select 
                        c.code,
                        c.name,
                        d.name,
                        d.id,
                        d.rounding,
                        case when COALESCE(c.currency_id,0) = 96 then SUM((case when COALESCE(a.debit, 0.0) != 0 then COALESCE(a.debit, 0.0) else 0 end)) else 0 end,
                        case when COALESCE(c.currency_id,0) = 96 then SUM((case when COALESCE(a.credit, 0.0) != 0 then COALESCE(a.credit, 0.0) else 0 end)) else 0 end,
                        case when COALESCE(c.currency_id,0) = 96 then SUM((case when COALESCE(a.debit, 0.0) != 0 then COALESCE(a.debit, 0.0) else 0 end)) else 0 end-
                        case when COALESCE(c.currency_id,0) = 96 then SUM((case when COALESCE(a.credit, 0.0) != 0 then COALESCE(a.credit, 0.0) else 0 end)) else 0 end,  
                
                        case when COALESCE(c.currency_id,0) != 96 then SUM((case when COALESCE(a.amount_currency, 0.0) > 0 then ABS(COALESCE(a.amount_currency, 0.0)) else 0 end)) else 0 end,
                        case when COALESCE(c.currency_id,0) != 96 then SUM((case when COALESCE(a.amount_currency, 0.0) < 0 then ABS(COALESCE(a.amount_currency, 0.0)) else 0 end)) else 0 end,
                        case when COALESCE(c.currency_id,0) != 96 then SUM((case when COALESCE(a.amount_currency, 0.0) < 0 then COALESCE(a.amount_currency, 0.0) else 0 end)) else 0 end+
                        case when COALESCE(c.currency_id,0) != 96 then SUM((case when COALESCE(a.amount_currency, 0.0) > 0 then COALESCE(a.amount_currency, 0.0) else 0 end)) else 0 end  
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
                        and b.id = %i
                        and d.id = %i
                        and a.date <= \'%s\'
                    group by 
                        c.code, c.name, c.currency_id,d.name,d.id,d.rounding""" %(account_type_id, currency_id, as_of_date))

            if sql == '':
                ss = ''

            self.env.cr.execute(sql)
            for row in self.env.cr.fetchall():
                res = {
                    'account_code': row[0] if row[0] else 0.0,
                    'account_name': row[1] if row[1] else '',
                    'currency_name': row[2] if row[2] else '',
                    'currency_id': row[3] if row[3] else 0.0,
                    'rounding': row[4] if row[4] else 0.0,
                    'tot_debit_kd': row[5] if row[5] else 0.0,
                    'tot_credit_kd': row[6] if row[6] else 0.0,
                    'balance_kd': row[7] if row[7] else 0.0,
                    'tot_debit_usd': row[8] if row[8] else 0.0,
                    'tot_credit_usd': row[9] if row[9] else 0.0,
                    'balance_usd': row[10] if row[10] else 0.0,
                }
                summary_data_list.append(res)

            return summary_data_list
        except Exception as e:
            logger.exception("get_detailed_data Method")
            raise ValidationError(e)

    def summary_data(self, as_of_date, account_type):
        try:
            summary_data_list = []

            if as_of_date == '':
                as_of_date = datetime.datetime.now()

            sql =("""select 
                    b.id,
                    b.name,
                    d.name,
                    d.id,
                    d.rounding,
                    
                    case when COALESCE(c.currency_id,0) = 96 then SUM((case when COALESCE(a.debit, 0.0) != 0 then COALESCE(a.debit, 0.0) else 0 end)) else 0 end,
                    case when COALESCE(c.currency_id,0) = 96 then SUM((case when COALESCE(a.credit, 0.0) != 0 then COALESCE(a.credit, 0.0) else 0 end)) else 0 end,
                    case when COALESCE(c.currency_id,0) = 96 then SUM((case when COALESCE(a.debit, 0.0) != 0 then COALESCE(a.debit, 0.0) else 0 end)) else 0 end-
                    case when COALESCE(c.currency_id,0) = 96 then SUM((case when COALESCE(a.credit, 0.0) != 0 then COALESCE(a.credit, 0.0) else 0 end)) else 0 end,  
            
                    case when COALESCE(c.currency_id,0) != 96 then SUM((case when COALESCE(a.amount_currency, 0.0) > 0 then ABS(COALESCE(a.amount_currency, 0.0)) else 0 end)) else 0 end,
                    case when COALESCE(c.currency_id,0) != 96 then SUM((case when COALESCE(a.amount_currency, 0.0) < 0 then ABS(COALESCE(a.amount_currency, 0.0)) else 0 end)) else 0 end,
                    case when COALESCE(c.currency_id,0) != 96 then SUM((case when COALESCE(a.amount_currency, 0.0) < 0 then COALESCE(a.amount_currency, 0.0) else 0 end)) else 0 end+
                    case when COALESCE(c.currency_id,0) != 96 then SUM((case when COALESCE(a.amount_currency, 0.0) > 0 then COALESCE(a.amount_currency, 0.0) else 0 end)) else 0 end  
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
                    and a.date <= \'%s\'
                    and b.id = (case when %s != 0 then %s else b.id end)
                group by 
                    b.id, b.name, c.currency_id,d.name,d.id,d.rounding
                order by
                    b.id""" % (as_of_date, account_type, account_type))

            self.env.cr.execute(sql)
            for row in self.env.cr.fetchall():
                res = {
                    'account_type_id': row[0] if row[0] else 0.0,
                    'account_type': row[1] if row[1] else '',
                    'currency_name': row[2] if row[2] else '',
                    'currency_id': row[3] if row[3] else 0.0,
                    'rounding': row[4] if row[4] else 0.0,
                    'tot_debit_kd': row[5] if row[5] else 0.0,
                    'tot_credit_kd': row[6] if row[6] else 0.0,
                    'balance_kd': row[7] if row[7] else 0.0,
                    'tot_debit_usd': row[8] if row[8] else 0.0,
                    'tot_credit_usd': row[9] if row[9] else 0.0,
                    'balance_usd': row[10] if row[10] else 0.0,
                    'as_of_date': as_of_date,
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

            as_of_date = data['as_of_date']
            account_type = data['account_type']

            docs = self.summary_data(as_of_date, account_type)

            if as_of_date == '':
                report_title = "(As Of Date: " + (datetime.date.today()).strftime(
                '%Y-%m-%d') + ")"
            else:
                report_title = "(As Of Date: " + as_of_date + ")"

            docargs = {
                'doc_ids': docids,
                'doc_model': 'account.move.line',
                'docs': docs,
                'title': report_title,
                'get_detailed_data': self.get_detailed_data,
            }
            return docargs
        except Exception as e:
            logger.exception("Get Report Values Method")
            raise ValidationError(e)