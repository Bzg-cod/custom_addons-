import io
import xlsxwriter
from odoo import models, fields, api
from datetime import datetime,date
import base64
import logging
from xlsxwriter.utility import xl_col_to_name

_logger = logging.getLogger(__name__)

class PayrollReportWizard(models.TransientModel):
    _name = 'payroll.report.wizard'
    _description = 'Payroll Report Wizard'

    name = fields.Char(string='File Name', default='Payroll Report.xlsx')
    data = fields.Binary(string='File', readonly=True)
    state = fields.Selection([('choose', 'Choose'), ('get', 'Get')], default='choose')
    employee_id = fields.Many2many('hr.employee', string='Employee')
    department_id = fields.Many2many('hr.department', string='Department')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    salary_rule_id = fields.Many2many('hr.salary.rule', string='Salary Rule')
    is_pension_id_included = fields.Boolean(string='Include Pension Number', default=False)
    report_format = fields.Selection([
        ('pdf', 'PDF'),
        ('xlsx', 'XLSX')
    ], string='Report Format', default='xlsx')
    @api.onchange('department_id')
    def _onchange_department_id(self):
        if self.department_id:
            # Fetch employees belonging to the selected departments
            employees = self.env['hr.employee'].search([('department_id', 'in', self.department_id.ids)])
            # Only update employee_id if it's empty to avoid overwriting user edits
            if not self.employee_id:
                self.employee_id = employees
        else:
            # If no departments are selected, do not clear employee_id to preserve editability
            pass

    def action_print(self):
        # Prepare domain for filtering payslips
        domain = []
        if self.employee_id:
            domain.append(('employee_id', 'in', self.employee_id.ids))
        if self.department_id:
            domain.append(('employee_id.department_id', 'in', self.department_id.ids))
        if self.start_date:
            domain.append(('date_from', '>=', self.start_date))
        if self.end_date:
            domain.append(('date_to', '<=', self.end_date))
        if self.salary_rule_id:
            domain.append(('line_ids.salary_rule_id', 'in', self.salary_rule_id.ids))

        # Fetch payslip data
        payslips = self.env['hr.payslip'].search(domain)
        # Get salary rules: use selected rules if provided, otherwise all rules from payslips, sorted by sequence
        salary_rules = self.salary_rule_id if self.salary_rule_id else payslips.mapped('line_ids.salary_rule_id').sorted(key=lambda x: x.sequence)
        salary_rule_names = [rule.name for rule in salary_rules]

        # Prepare report data
        report_data = []
        for payslip in payslips:
            valid_lines = payslip.line_ids.filtered(
                lambda line: not self.salary_rule_id or line.salary_rule_id.id in self.salary_rule_id.ids
            )
            if valid_lines:
                # Create a dictionary of salary rule amounts
                rule_amounts = {rule.name: 0.0 for rule in salary_rules}
                for line in valid_lines:
                    if line.salary_rule_id.name in rule_amounts:
                        rule_amounts[line.salary_rule_id.name] = line.total
                # Calculate total for the row
                row_total = sum(rule_amounts.values())
                report_data.append({
                    'employee': payslip.employee_id.name,
                    'tin_number': payslip.employee_id.tin_number or '',
                    'pension_number': payslip.employee_id.pension_number or '',
                    'start_date': payslip.date_from,
                    'end_date': payslip.date_to,
                    'rule_amounts': rule_amounts,
                    'total': row_total,
                })

        if self.report_format == 'xlsx':
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            sheet = workbook.add_worksheet('Payroll Report')
            bold = workbook.add_format({'bold': True, 'align': 'left'})
            currency_format = workbook.add_format({'num_format': '#,##0.00', 'align': 'right'})
            title_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14})
            subtitle_format = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 12})
            header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'align': 'left'})
            total_format = workbook.add_format({'bold': True, 'align': 'left', 'bg_color': '#D3D3D3'})
            currency_total_format = workbook.add_format({'bold': True, 'num_format': '#,##0.00', 'align': 'right', 'bg_color': '#D3D3D3'})

            # Dynamic report subtitle
            if self.start_date and self.end_date:
                report_subtitle = f"{self.start_date.strftime('%B %d/%Y')} - {self.end_date.strftime('%B %d/%Y')}"
            else:
                report_subtitle = datetime.now().strftime('%B %d/%Y')

            # Calculate total columns: SN, Employee, TIN Number, optional Pension Number, salary rules, Total
            pension_col_offset = 1 if self.is_pension_id_included else 0
            total_columns = 3 + pension_col_offset + len(salary_rule_names) + 1  # +1 for Total column
            end_column = xl_col_to_name(total_columns - 1)  # 0-based index for last column

            # Write title and subtitle
            sheet.merge_range(f'A1:{end_column}1', 'Payroll Report', title_format)
            sheet.merge_range(f'A2:{end_column}2', report_subtitle, subtitle_format)
            sheet.set_row(0, 20)
            sheet.set_row(1, 20)

            # Write departments
            departments = ', '.join(self.department_id.mapped('name')) if self.department_id else 'All Departments'
            sheet.merge_range(f'A3:{end_column}3', f"Departments: {departments}", bold)
            sheet.set_row(2, 20)

            # Define headers with SN, Employee, TIN Number, optional Pension Number, salary rule columns, and Total
            headers = ['SN', 'Employee', 'TIN Number']
            if self.is_pension_id_included:
                headers.append('Pension Number')
            headers.extend(salary_rule_names)
            headers.append('Total')
            header_row = 4
            for col, header in enumerate(headers):
                sheet.write(header_row, col, header, header_format)

            # Set column widths
            column_widths = [5, 30, 15]
            if self.is_pension_id_included:
                column_widths.append(15)
            column_widths.extend([15] * len(salary_rule_names))
            column_widths.append(15)  # Width for Total column
            for col, width in enumerate(column_widths):
                sheet.set_column(col, col, width)

            # Initialize totals
            total_amounts = {rule: 0.0 for rule in salary_rule_names}
            total_sum = 0.0
            serial_number = 1

            # Write data
            row = header_row + 1
            for record in report_data:
                sheet.write(row, 0, serial_number)
                sheet.write(row, 1, record['employee'])
                sheet.write(row, 2, record['tin_number'])
                col_offset = 3
                if self.is_pension_id_included:
                    sheet.write(row, col_offset, record['pension_number'])
                    col_offset += 1
                for col, rule in enumerate(salary_rule_names, col_offset):
                    amount = record['rule_amounts'].get(rule, 0.0)
                    sheet.write(row, col, amount, currency_format)
                    total_amounts[rule] += amount
                # Write row total
                sheet.write(row, col_offset + len(salary_rule_names), record['total'], currency_format)
                total_sum += record['total']
                row += 1
                serial_number += 1

            # Write total row
            if report_data:
                total_label_col = 1 if not self.is_pension_id_included else 2
                sheet.write(row, total_label_col, 'Total', total_format)
                col_offset = 3 if not self.is_pension_id_included else 4
                for col, rule in enumerate(salary_rule_names, col_offset):
                    sheet.write(row, col, total_amounts[rule], currency_total_format)
                sheet.write(row, col_offset + len(salary_rule_names), total_sum, currency_total_format)

            # Save and close workbook
            workbook.close()
            output.seek(0)
            file_data = output.getvalue()
            output.close()

            # Store file as attachment
            self.write({
                'data': base64.b64encode(file_data),
                'state': 'get',
                'name': 'Payroll Report.xlsx'
            })

            # Return action to open the download form
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'payroll.report.wizard',
                'view_mode': 'form',
                'res_id': self.id,
                'views': [(False, 'form')],
                'target': 'new',
            }
  