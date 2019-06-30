# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportTrialBalance(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_trialbalance'

    def _get_accounts(self, accounts, display_account):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
        """

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"','')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
                   " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            if account.id in account_result:
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
            if display_account == 'movement' and (not currency.is_zero(res['debit']) or not currency.is_zero(res['credit'])):
                account_res.append(res)
        return account_res


    def _get_accounts_by_type(self):

        account_result = []
        # # Prepare sql query base on selected parameters from wizard
        # tables, where_clause, where_params = self.env['account.move.line']._query_get()
        # tables = tables.replace('"','')
        # if not tables:
        #     tables = 'account_move_line'
        # wheres = [""]
        # if where_clause.strip():
        #     wheres.append(where_clause.strip())
        # filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT B.internal_group as type, SUM(A.debit) AS debit, SUM(A.credit) AS credit, (SUM(A.debit) - SUM(A.credit)) AS balance" +\
                   " FROM account_move_line A, account_account B WHERE A.account_id = B.id GROUP BY B.internal_group order by 1")

        self.env.cr.execute(request)
        i = 0
        for row in self.env.cr.dictfetchall():
            # account_result[i] = row
            # i = i + 1
            account_result.append(row)
            # account_result['type'] = row['type']
            # account_result['debit'] = row['debit']
            # account_result['credit'] = row['credit']
            # account_result['balance'] = row['balance']


        # account_res = []
        # for account in accounts:
        #     res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
        #     currency = account.currency_id and account.currency_id or account.company_id.currency_id
        #     res['code'] = account.code
        #     res['name'] = account.name
        #     if account.id in account_result:
        #         res['debit'] = account_result[account.id].get('debit')
        #         res['credit'] = account_result[account.id].get('credit')
        #         res['balance'] = account_result[account.id].get('balance')
        #     if display_account == 'all':
        #         account_res.append(res)
        #     if display_account == 'not_zero' and not currency.is_zero(res['balance']):
        #         account_res.append(res)
        #     if display_account == 'movement' and (not currency.is_zero(res['debit']) or not currency.is_zero(res['credit'])):
        #         account_res.append(res)
        return account_result


    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
        group_by_type = data['form'].get('group_by_type')
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account)
        account_by_type_res = self._get_accounts_by_type()
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': account_res,
            'AccountsGrouping': account_by_type_res,
            'by_account_type': group_by_type,
        }
