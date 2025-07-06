from odoo import models, fields, api


class CustomContract(models.Model):

    _inherit="hr.contract"

    transportation_allowance = fields.Monetary(string="Transportation Allowance", help="Transportation Allowance")
    position_allowance = fields.Monetary(string="Position Allowance", help="Position Allowance")
    fuel_allowance = fields.Monetary(string="Fuel Allowance", help="Fuel Allowance")
    dessert_allowance = fields.Monetary(string="Dessert Allowance", help="Dessert Allowance")
    food_allowance = fields.Monetary(string="Food Allowance", help="Food Allowance")
    deligation_allowance = fields.Monetary(string="Deligation Allowance", help="Deligation Allowance")
    sefbox_allowance = fields.Monetary(string="SefBox Allowance", help="SefBox Allowance")
    house_allowance = fields.Monetary(string="House Allowance", help="House Allowance")
    other_allowance = fields.Monetary(string="Other Allowance", help="Other Allowance")
    busagon_ofa_allowance = fields.Monetary(string="Busagon Ofa Allowance", help="Busagon Ofa Allowance")
    cost_sharing_allowance = fields.Monetary(string="Cost Sharing Allowance", help="Cost Sharing Allowance")
    edir_allowance = fields.Monetary(string="Edir Allowance", help="Edir Allowance")

class CustomHrPayrollReportExtension(models.TransientModel):
    _inherit = 'custom.hr.payroll.report'  # Inherit the original model

    # Add the new field
    transportation_allowance = fields.Float(string="Transportation Allowance")
    position_allowance = fields.Float(string="Position Allowance")
    fuel_allowance = fields.Float(string="Fuel Allowance", help="Fuel Allowance")
    dessert_allowance = fields.Float(string="Dessert Allowance", help="Dessert Allowance")
    food_allowance = fields.Float(string="Food Allowance", help="Food Allowance")
    deligation_allowance = fields.Float(string="Deligation Allowance", help="Deligation Allowance")
    sefbox_allowance = fields.Float(string="SefBox Allowance", help="SefBox Allowance")
    house_allowance = fields.Float(string="House Allowance", help="House Allowance")
    other_allowance = fields.Float(string="Other Allowance", help="Other Allowance")
    busagon_ofa_allowance = fields.Float(string="Busagon Ofa Allowance", help="Busagon Ofa Allowance")
    cost_sharing_allowance = fields.Float(string="Cost Sharing Allowance", help="Cost Sharing Allowance")
    edir_allowance = fields.Float(string="Edir Allowance", help="Edir Allowance")

    # Override update_payslips to include transportation_allowance
    def update_payslips(self, payslip_lines):
        # Call the parent method to get the original payroll_amount dictionary
        payroll_amount = super(CustomHrPayrollReportExtension, self).update_payslips(payslip_lines)
        
        # Add transportation_allowance logic
        for line in payslip_lines:
            if line.code == 'TRANSALLOW':  # Define a unique code for transportation allowance
                payroll_amount["transportation_allowance"] = line.amount
            if line.code == 'POSALLOW':  # Define a unique code for transportation allowance
                payroll_amount["position_allowance"] = line.amount
            if line.code == 'FUELALLOW':  # Define a unique code for transportation allowance
                payroll_amount["fuel_allowance"] = line.amount
            if line.code == 'DESALLOW':  # Define a unique code for transportation allowance
                payroll_amount["dessert_allowance"] = line.amount
            if line.code == 'POSALLOW':  # Define a unique code for transportation allowance
                payroll_amount["food_allowance"] = line.amount
            if line.code == 'DELALLOW':  # Define a unique code for transportation allowance
                payroll_amount["deligation_allowance"] = line.amount
            if line.code == 'SEFALLOW':  # Define a unique code for transportation allowance
                payroll_amount["sefbox_allowance"] = line.amount
            if line.code == 'HOUSEALLOW':  # Define a unique code for transportation allowance
                payroll_amount["house_allowance"] = line.amount
            if line.code == 'OTHERALLOW':  # Define a unique code for transportation allowance
                payroll_amount["other_allowance"] = line.amount
            if line.code == 'BUSAGONALLOW':  # Define a unique code for transportation allowance
                payroll_amount["busagon_ofa_allowance"] = line.amount
            if line.code == 'COSTALLOW':  # Define a unique code for transportation allowance
                payroll_amount["cost_sharing_allowance"] = line.amount
            if line.code == 'EDIRALLOW':  # Define a unique code for transportation allowance
                payroll_amount["edir_allowance"] = line.amount
        
        return payroll_amount

    # Override fetch_and_update_report to include transportation_allowance
    def fetch_and_update_report(self, date_from, date_to, department_id):
        # Call the parent method to handle the original logic
        super(CustomHrPayrollReportExtension, self).fetch_and_update_report(date_from, date_to, department_id)
        
        # Since fetch_and_update_report creates records, we need to ensure the new field is included
        # The parent method already creates records, so we just need to update the payroll_amount
        # This is handled in update_payslips, so no additional logic is needed here unless you want to modify existing records

    # Optionally override print_pdf_report if the report needs to display the new field
    def print_pdf_report(self):
        # Call the parent method
        action = super(CustomHrPayrollReportExtension, self).print_pdf_report()
        
        # If the report needs to reflect transportation_allowance, ensure the context or report template is updated
        # This depends on your hr.payroll.report1 model/report, so adjust accordingly
        return action

    # No need to override refresh_report, confirm_payslip_status, or return_payslip_detail
    # unless they specifically need to handle transportation_allowance