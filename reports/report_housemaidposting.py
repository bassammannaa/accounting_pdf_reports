# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
import datetime


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
