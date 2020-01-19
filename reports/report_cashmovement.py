# -*- coding: utf-8 -*-

from odoo import models, api
import logging
from odoo.exceptions import ValidationError
from datetime import date, datetime
import datetime

logger = logging.getLogger(__name__)


class ReportCashMovement(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_cashmovement'
    _description = "Cash Movement"

    def detail_data(self, account_id, from_date, to_date):
        try:
            summary_data_list = []

            if from_date == '':
                from_date = datetime.datetime.now()
            if to_date == '':
                to_date = datetime.datetime.now()

            sql = ("""select
                            a."date",
                            b.external_office_id,
                            COALESCE(a.debit, 0.0),
                            COALESCE(a.credit, 0.0),
                            a."name",
                            e."name",
                            d."name"
                        
                        from 
                            account_move_line a,
                            housemaid_applicant_applications b,
                            account_journal c,
                            account_account d,
                            res_partner e
                        
                        where
                            a.application_id = b.id
                            and a.journal_id = c.id
                            and a.account_id = d.id
                            and a.partner_id = e.id
                            and a.date between \'%s\' and \'%s\'
                            and d.id = %i
                            and d.internal_type = 'liquidity'""" % (from_date, to_date, account_id))

            self.env.cr.execute(sql)
            for row in self.env.cr.fetchall():
                res = {
                    'tran_date': row[0] if row[0] else '',
                    'external_office_id': row[1] if row[1] else '',
                    'cash_in': row[2] if row[2] else 0.0,
                    'cash_out': row[3] if row[3] else 0.0,
                    'tran_ref': row[4] if row[4] else '',
                    'sponsor': row[5] if row[5] else '',
                    'account': row[6] if row[6] else '',
                }
                summary_data_list.append(res)

            return summary_data_list
        except Exception as e:
            logger.exception("summary_data Method")
            raise ValidationError(e)

    def summary_data(self, from_date, to_date):
        try:
            summary_data_list = []

            if from_date == '':
                from_date = datetime.datetime.now()
            if to_date == '':
                to_date = datetime.datetime.now()

            sql = ("""select distinct
                            d.id,
                            d.name
                        from 
                            account_move_line a,
                            housemaid_applicant_applications b,
                            account_journal c,
                            account_account d,
                            res_partner e

                        where
                            a.application_id = b.id
                            and a.journal_id = c.id
                            and a.account_id = d.id
                            and a.partner_id = e.id
                            and a.date between \'%s\' and \'%s\'
                            and d.internal_type = 'liquidity'""" % (from_date, to_date))

            self.env.cr.execute(sql)
            for row in self.env.cr.fetchall():
                res = {
                    'account_id': row[0] if row[0] else 0.0,
                    'account_name': row[1] if row[1] else '',
                    'from_date': from_date,
                    'to_date': to_date,
                }
                summary_data_list.append(res)

            return summary_data_list
        except Exception as e:
            logger.exception("summary_data Method")
            raise ValidationError(e)

    @api.model
    def _get_report_values(self, docids, data=None):
        docargs = []
        domain = []
        report_title = ''

        from_date = data['from_date']
        to_date = data['to_date']

        docs = self.summary_data(from_date, to_date)

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account_move_line',
            'docs': docs,
            'detail_data': self.detail_data,
        }
        return docargs
