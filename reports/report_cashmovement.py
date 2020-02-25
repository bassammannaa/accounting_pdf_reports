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

    def summary_data(self, from_date, to_date, journal_id):
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
                            and c.id = (case when %i = 0 then c.id else %i end)
                            and a.date between \'%s\' and \'%s\'
                            and d.internal_type = 'liquidity'""" % (journal_id, journal_id, from_date, to_date))

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
        journal_id = data['journal_ids']

        docs = self.summary_data(from_date, to_date, journal_id)

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account_move_line',
            'docs': docs,
            'detail_data': self.detail_data,
        }
        return docargs


class ReportCashMovementExcel(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_cashmovement_excel'
    _inherit = 'report.report_xlsx.abstract'
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

    def summary_data(self, from_date, to_date, journal_id):
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
                            and c.id = (case when %i = 0 then c.id else %i end)
                            and a.date between \'%s\' and \'%s\'
                            and d.internal_type = 'liquidity'""" % (journal_id, journal_id, from_date, to_date))

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
    def generate_xlsx_report(self, workbook, data, wizard):
        try:

            def get_date_format(date):
                if date:
                    # date = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
                    date = date.strftime('%Y-%m-%d')
                return date


            from_date = data['from_date']
            to_date = data['to_date']
            journal_id = data['journal_ids']

            accounts_list = self.summary_data(from_date, to_date, journal_id)

            # Pre-Format
            header_line_format_string = workbook.add_format(
                {'bold': True, 'left': 1, 'font_size': 12, 'text_wrap': 0, 'bg_color': '#e7e3e2'})
            header_line_format_num = workbook.add_format(
                {'bold': True, 'right': 1, 'font_size': 12, 'text_wrap': 0, 'bg_color': '#e7e3e2'})

            normal_line_format_string_nowrap = workbook.add_format(
                {'bold': False, 'left': 1, 'font_size': 10, 'text_wrap': 0})
            normal_line_format_string_wrap = workbook.add_format(
                {'bold': False, 'left': 1, 'font_size': 10, 'text_wrap': 1})

            normal_line_format_num_KWD = workbook.add_format(
                {'bold': False, 'right': 1, 'font_size': 10, 'text_wrap': 0, 'num_format': '#,##0.000'})
            normal_line_format_num_USD = workbook.add_format(
                {'bold': False, 'right': 1, 'font_size': 10, 'text_wrap': 0, 'num_format': '#,##0.00'})

            for account in accounts_list:
                current_row = 0
                sheet = workbook.add_worksheet("%s" % account.get('account_name', ''))

                accounts_details_list = self.detail_data(account.get('account_id', ''), from_date, to_date)

                sheet.write(current_row, 0, 'Transaction Date', header_line_format_string)
                sheet.set_column(0, 0, 20)

                sheet.write(current_row, 1, 'Code', header_line_format_string)
                sheet.set_column(1, 1, 20)

                sheet.write(current_row, 2, 'Transaction Ref', header_line_format_string)
                sheet.set_column(2, 2, 25)

                sheet.write(current_row, 3, 'Sponsor Name', header_line_format_num)
                sheet.set_column(3, 3, 25)

                sheet.write(current_row, 4, 'Cash In', header_line_format_num)
                sheet.set_column(4, 4, 15)

                sheet.write(current_row, 5, 'Cash Out', header_line_format_num)
                sheet.set_column(5, 5, 15)

                sheet.autofilter('A1:F1')


                for account_details in accounts_details_list:
                    current_row += 1
                    sheet.write(current_row, 0, get_date_format(account_details.get('tran_date','')),normal_line_format_string_nowrap)
                    sheet.write(current_row, 1, account_details.get('external_office_id', ''), normal_line_format_string_nowrap)
                    sheet.write(current_row, 2, account_details.get('tran_ref', ''), normal_line_format_string_nowrap)
                    sheet.write(current_row, 3, account_details.get('sponsor', ''), normal_line_format_num_USD)
                    sheet.write(current_row, 4, account_details.get('cash_in', ''), normal_line_format_num_KWD)
                    sheet.write(current_row, 5, account_details.get('cash_out', ''), normal_line_format_num_KWD)

        except Exception as e:
            logger.exception("generate_xlsx_report Method")
            raise ValidationError(e)