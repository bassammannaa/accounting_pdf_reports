# -*- coding: utf-8 -*-

from odoo import models, api
import logging
from odoo.exceptions import ValidationError
from datetime import date, datetime
import datetime

logger = logging.getLogger(__name__)


class ReportHousemaidPosting(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_housemaidposting'
    _description = "Housemaid Posting"

    def total_comparison(self, account_id, from_date, to_date):
        results=[]

        if from_date and to_date:
            from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d')
            to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d')
            date_between = ' And date between \'' + str(from_date_obj) + '\' and \'' + str(to_date_obj) + '\''

        sql = 'select b.external_office_id, b.state, SUM(COALESCE(a.debit, 0.0)), SUM(COALESCE(a.credit, 0.0)), '
        sql += 'SUM(COALESCE(a.debit, 0.0)) - SUM(COALESCE(a.credit, 0.0)) '
        sql += 'From  account_move_line a, housemaid_applicant_applications b '
        sql += 'Where  a.application_id = b.id '
        #sql += date_between + ' '
        sql += 'And a.account_id = ' + str(account_id) + ' '
        sql += 'group by b.state, b.external_office_id '
        sql += 'Having SUM(COALESCE(a.debit, 0.0)) <> SUM(COALESCE(a.credit, 0.0))'

        self.env.cr.execute(sql)
        for row in self.env.cr.fetchall():
            res = {
                'office': row[0] if row[0] else '',
                'state': row[1] if row[1] else '',
                'total_debit': row[2] if row[2] else 0.0,
                'total_credit': row[3] if row[3] else 0.0,
                'total_balance': row[4] if row[4] else 0.0,
            }
            results.append(res)
        return results

    @api.model
    def _get_report_values(self, docids, data=None):

        comparison_flag = False

        if data['application_comparison'] == False:

            search_domain = []
            docs_comparison = None
            comparison_flag = False

            if data['link_to_application'] == True:
                search_domain.append(('application_id', '!=', False))
            else:
                search_domain.append(('application_id', '=', False))

            if data['from_date']:
                search_domain.append(('date', '>=', data['from_date']))

            if data['to_date']:
                search_domain.append(('date', '<=', data['to_date']))

            if data['selected_account']:
                search_domain.append(('account_id', '=', data['selected_account']))

            if data['posting_type'] == 'dr':
                search_domain.append(('debit', '>', 0))

            if data['posting_type'] == 'cr':
                search_domain.append(('credit', '>', 0))

            docs = self.env['account.move.line'].search(search_domain, order='application_id asc')
        else:
            docs = None
            docs_comparison = self.total_comparison(data['selected_account'], data['from_date'], data['to_date'])
            comparison_flag = True

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account_move_line',
            'docs': docs,
            'docs_comparison': docs_comparison,
            'comparison_flag': comparison_flag,
        }
        return docargs


class ReportHousemaidPostingExcel(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_housemaidposting_excel'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Housemaid Posting"

    def total_comparison(self, account_id, from_date, to_date):
        results=[]

        if from_date and to_date:
            from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d')
            to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d')
            date_between = ' And date between \'' + str(from_date_obj) + '\' and \'' + str(to_date_obj) + '\''

        sql = 'select b.external_office_id, b.state, SUM(COALESCE(a.debit, 0.0)), SUM(COALESCE(a.credit, 0.0)), '
        sql += 'SUM(COALESCE(a.debit, 0.0)) - SUM(COALESCE(a.credit, 0.0)) '
        sql += 'From  account_move_line a, housemaid_applicant_applications b '
        sql += 'Where  a.application_id = b.id '
        #sql += date_between + ' '
        sql += 'And a.account_id = ' + str(account_id) + ' '
        sql += 'group by b.state, b.external_office_id '
        sql += 'Having SUM(COALESCE(a.debit, 0.0)) <> SUM(COALESCE(a.credit, 0.0))'

        self.env.cr.execute(sql)
        for row in self.env.cr.fetchall():
            res = {
                'office': row[0] if row[0] else '',
                'state': row[1] if row[1] else '',
                'total_debit': row[2] if row[2] else 0.0,
                'total_credit': row[3] if row[3] else 0.0,
                'total_balance': row[4] if row[4] else 0.0,
            }
            results.append(res)
        return results

    @api.model
    def generate_xlsx_report(self, workbook, data, wizard):
        try:
            account_move_line_obj = account_move_line_compare_obj = None

            search_domain = []

            if data['link_to_application'] == True:
                search_domain.append(('application_id', '!=', False))
            else:
                search_domain.append(('application_id', '=', False))

            if data['from_date']:
                search_domain.append(('date', '>=', data['from_date']))

            if data['to_date']:
                search_domain.append(('date', '<=', data['to_date']))

            if data['selected_account']:
                search_domain.append(('account_id', '=', data['selected_account']))

            if data['posting_type'] == 'dr':
                search_domain.append(('debit', '>', 0))

            if data['posting_type'] == 'cr':
                search_domain.append(('credit', '>', 0))

            account_move_line_obj = self.env['account.move.line'].search(search_domain, order='application_id asc')

            account_move_line_compare_obj = self.total_comparison(data['selected_account'], data['from_date'],
                                                          data['to_date'])

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

            current_row = 0
            sheet = workbook.add_worksheet('Housemaid Posting Details')

            sheet.write(current_row, 0, 'Code', header_line_format_string)
            sheet.set_column(0, 0, 25)

            sheet.write(current_row, 1, 'Transaction Name', header_line_format_string)
            sheet.set_column(1, 1, 25)

            sheet.write(current_row, 2, 'Transaction Ref', header_line_format_string)
            sheet.set_column(2, 2, 25)

            sheet.write(current_row, 3, 'EQ Amount', header_line_format_num)
            sheet.set_column(3, 3, 25)

            sheet.write(current_row, 4, 'Credit Amount(KWD)', header_line_format_num)
            sheet.set_column(4, 4, 20)

            sheet.write(current_row, 5, 'Debit Amount(KWD)', header_line_format_num)
            sheet.set_column(5, 5, 20)

            sheet.write(current_row, 6, 'Balance (KWD)', header_line_format_num)
            sheet.set_column(6, 6, 20)

            sheet.autofilter('A1:G1')

            for account_move_line in account_move_line_obj:
                current_row += 1
                sheet.write(current_row, 0, account_move_line.application_id.external_office_id , normal_line_format_string_nowrap)
                sheet.write(current_row, 1, account_move_line.move_id.name, normal_line_format_string_nowrap)
                sheet.write(current_row, 2, account_move_line.ref, normal_line_format_string_nowrap)
                sheet.write(current_row, 3, account_move_line.amount_currency, normal_line_format_num_USD)
                sheet.write(current_row, 4, account_move_line.debit, normal_line_format_num_KWD)
                sheet.write(current_row, 5, account_move_line.credit, normal_line_format_num_KWD)
                sheet.write(current_row, 6, account_move_line.balance, normal_line_format_num_KWD)



        except Exception as e:
            logger.exception("generate_xlsx_report Method")
            raise ValidationError(e)




