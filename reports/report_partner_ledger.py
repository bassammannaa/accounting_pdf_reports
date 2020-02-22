# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class ReportPartnerLedger(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_partnerledger'
    _description = "Partner Ledger"

    def _lines(self, data, partner):
        full_account = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """
            SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                ORDER BY "account_move_line".date"""
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        sum = 0.0
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for r in res:
            r['date'] = r['date']
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id'))
            full_account.append(r)
        return full_account

    def _sum_partner(self, data, partner, field):
        if field not in ['debit', 'credit', 'debit - credit', 'amount_currency']:
            return
        result = 0.0
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '

        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """SELECT sum(""" + field + """)
                FROM """ + query_get_data[0] + """, account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state IN %s
                    AND account_id IN %s
                    AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        data['computed'] = {}

        result_partner_sponsor = data['form']['partner_sponsor']
        result_partner_external_offfice = data['form']['partner_external_offfice']

        obj_partner = self.env['res.partner']

        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')

        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.internal_type IN %s
            AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))

        selected_account = data['form'].get('selected_account', True)
        if selected_account:
            data['computed']['account_ids'] = tuple([selected_account])
        else:
            data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]

        detailed_value = data['form'].get('detailed', True)

        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        query = """
            SELECT DISTINCT "account_move_line".partner_id
            FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
            WHERE "account_move_line".partner_id IS NOT NULL
                AND "account_move_line".account_id = account.id
                AND am.id = "account_move_line".move_id
                AND am.state IN %s
                AND "account_move_line".account_id IN %s
                AND NOT account.deprecated
                AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))
        partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]

        if result_partner_sponsor:
            partners = obj_partner.browse(result_partner_sponsor)
        elif result_partner_external_offfice:
            partners = obj_partner.browse(result_partner_external_offfice)
        else:
            partners = obj_partner.browse(partner_ids)

        partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))


        return {
            'doc_ids': partner_ids,
            'doc_model': self.env['res.partner'],
            'data': data,
            'docs': partners,
            'detailed': 1 if detailed_value else 0,
            'time': time,
            'lines': self._lines,
            'sum_partner': self._sum_partner,
        }


class PartnerLedgerReportXlsx(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_partnerledger_excel'
    _inherit = 'report.report_xlsx.abstract'


    def _sum_partner(self, data, partner, field):
        if field not in ['debit', 'credit', 'debit - credit', 'amount_currency']:
            return
        result = 0.0
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '

        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """SELECT sum(""" + field + """)
                FROM """ + query_get_data[0] + """, account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state IN %s
                    AND account_id IN %s
                    AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    def get_main_partner_list(self, data):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        data['computed'] = {}

        result_partner_sponsor = data['form']['partner_sponsor']
        result_partner_external_offfice = data['form']['partner_external_offfice']

        obj_partner = self.env['res.partner']

        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')

        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.internal_type IN %s
            AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))

        selected_account = data['form'].get('selected_account', True)
        if selected_account:
            data['computed']['account_ids'] = tuple([selected_account])
        else:
            data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]

        detailed_value = data['form'].get('detailed', True)

        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        query = """
            SELECT DISTINCT "account_move_line".partner_id
            FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
            WHERE "account_move_line".partner_id IS NOT NULL
                AND "account_move_line".account_id = account.id
                AND am.id = "account_move_line".move_id
                AND am.state IN %s
                AND "account_move_line".account_id IN %s
                AND NOT account.deprecated
                AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))
        partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]

        if result_partner_sponsor:
            partners = obj_partner.browse(result_partner_sponsor)
        elif result_partner_external_offfice:
            partners = obj_partner.browse(result_partner_external_offfice)
        else:
            partners = obj_partner.browse(partner_ids)

        partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))

        return partners

    def _lines(self, data, partner):
        full_account = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """
            SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, ("account_move_line".debit - "account_move_line".credit) balance, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code, app.external_office_id
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN housemaid_applicant_applications app ON ("account_move_line".application_id=app.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                ORDER BY "account_move_line".date"""
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        sum = 0.0
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for r in res:
            r['date'] = r['date']
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id'))
            full_account.append(r)
        return full_account


    def generate_xlsx_report(self, workbook, data, wizard):

        def get_date_format(date):
            if date:
                # date = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
                date = date.strftime('%Y-%m-%d')
            return date

        # Pre-Format
        header_line_format_string = workbook.add_format({'bold': True, 'left': 1, 'font_size': 12, 'text_wrap': 0, 'bg_color': '#e7e3e2'})
        header_line_format_num = workbook.add_format({'bold': True, 'right': 1, 'font_size': 12, 'text_wrap': 0, 'bg_color': '#e7e3e2'})

        normal_line_format_string_nowrap = workbook.add_format({'bold': False, 'left': 1, 'font_size': 10, 'text_wrap': 0})
        normal_line_format_string_wrap = workbook.add_format(
            {'bold': False, 'left': 1, 'font_size': 10, 'text_wrap': 1})

        normal_line_format_num_KWD = workbook.add_format(
            {'bold': False, 'right': 1, 'font_size': 10, 'text_wrap': 0, 'num_format': '#,##0.000'})
        normal_line_format_num_USD = workbook.add_format(
            {'bold': False, 'right': 1, 'font_size': 10, 'text_wrap': 0, 'num_format': '#,##0.00'})


        # Data Object
        partners_obj = self.get_main_partner_list(data)

        sheet = workbook.add_worksheet('Partners Summary')
        # First line
        current_row = 0

        sheet.write(current_row, 0, 'Sponsor Name',header_line_format_string)
        sheet.set_column(0, 0, 18)

        sheet.write(current_row, 1, 'Debit (KWD)', header_line_format_num)
        sheet.set_column(1, 1, 13)

        sheet.write(current_row, 2, 'Credit (KWD)', header_line_format_num)
        sheet.set_column(2, 2, 13)

        sheet.write(current_row, 3, 'Balance (KWD)', header_line_format_num)
        sheet.set_column(3, 3, 18)

        sheet.write(current_row, 4, 'Currency (USD)', header_line_format_num)
        sheet.set_column(4, 4, 18)

        sheet.autofilter('A1:E1')

        current_row += 1
        for partner in partners_obj:
            sheet.write(current_row, 0, partner.name, normal_line_format_string_nowrap)
            sheet.write(current_row, 1, self._sum_partner(data, partner, 'debit'), normal_line_format_num_KWD)
            sheet.write(current_row, 2, self._sum_partner(data, partner, 'credit'), normal_line_format_num_KWD)
            sheet.write(current_row, 3, self._sum_partner(data, partner, 'debit - credit'), normal_line_format_num_KWD)
            sheet.write(current_row, 4, self._sum_partner(data, partner, 'amount_currency'), normal_line_format_num_KWD)
            current_row += 1


        # Add new Excel Sheet <<Partners Details>>
        #============================================
        sheet = workbook.add_worksheet('Partners Details')
        # First line
        current_row = 0

        sheet.write(current_row, 0, 'Date', header_line_format_string)
        sheet.set_column(0, 0, 8)

        sheet.write(current_row, 1, 'JRNL', header_line_format_string)
        sheet.set_column(1, 1, 5)

        sheet.write(current_row, 2, 'Account Code', header_line_format_string)
        sheet.set_column(2, 2, 15)

        sheet.write(current_row, 3, 'Housemaid', header_line_format_string)
        sheet.set_column(3, 3, 15)

        sheet.write(current_row, 4, 'Sponsor Name',header_line_format_string)
        sheet.set_column(4, 4, 18)

        sheet.write(current_row, 5, 'Reference',header_line_format_string)
        sheet.set_column(5, 5, 35)

        sheet.write(current_row, 6, 'Debit (KWD)', header_line_format_num)
        sheet.set_column(6, 6, 13)

        sheet.write(current_row, 7, 'Credit (KWD)', header_line_format_num)
        sheet.set_column(7, 7, 13)

        sheet.write(current_row, 8, 'Balance (KWD)', header_line_format_num)
        sheet.set_column(8, 8, 18)

        sheet.write(current_row, 9, 'Currency (USD)', header_line_format_num)
        sheet.set_column(9, 9, 18)

        sheet.autofilter('A1:J1')

        current_row += 1
        for partner in partners_obj:
            lines = self._lines(data, partner)
            for line in lines:
                sheet.write(current_row, 0, get_date_format(line.get('date', '')), normal_line_format_string_nowrap)
                sheet.write(current_row, 1, line.get('code', ''), normal_line_format_string_nowrap)
                sheet.write(current_row, 2, line.get('a_code', '') + '-' + line.get('a_name', ''), normal_line_format_string_nowrap)
                sheet.write(current_row, 3, line.get('external_office_id', ''), normal_line_format_string_nowrap)
                sheet.write(current_row, 4, partner.name, normal_line_format_string_nowrap)
                sheet.write(current_row, 5, line.get('displayed_name', ''), normal_line_format_string_wrap)
                sheet.write(current_row, 6, line.get('debit', ''), normal_line_format_num_KWD)
                sheet.write(current_row, 7, line.get('credit', ''), normal_line_format_num_KWD)
                sheet.write(current_row, 8, line.get('balance', ''), normal_line_format_num_KWD)
                sheet.write(current_row, 9, line.get('amount_currency', ''), normal_line_format_num_USD)
                current_row += 1







