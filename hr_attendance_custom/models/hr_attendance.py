from odoo import models, fields, api

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    is_approved = fields.Boolean(string="Approved", default=False)
    status = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
        ],
        string="Status",
        default="pending"
    )

    def action_approve_attendance_1(self):
        for rec in self:
            rec.is_approved = True
            rec.status = 'approved'  
        
