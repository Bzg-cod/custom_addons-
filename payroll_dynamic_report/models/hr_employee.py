from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    tin_number = fields.Char(string='TIN Number', help='Tax Identification Number')
    pension_number = fields.Char(string='Pension Number', help='Pension Identification Number')