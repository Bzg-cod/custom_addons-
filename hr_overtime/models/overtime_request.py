from odoo import models, fields, api
from datetime import datetime

from odoo.exceptions import ValidationError


class OvertimeRequest(models.Model):
    _name = 'overtime.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "requested_by"
    requested_by = fields.Many2one('hr.employee', string="Requested By",required=True, tracking=True, )
    requesting_reason = fields.Html(string="Reason")
    start_date = fields.Datetime(string="Start Date",tracking=True,)
    end_date = fields.Datetime(string="End Date",tracking=True,)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('review', 'Review'),
        ('reject', 'Rejected'),
        ('approve', 'Approved'),
    ], string="state", default="draft", tracking=True)
    review_by = fields.Many2one('res.users', string="Review By", tracking=True, )
    approve_by = fields.Many2one('res.users', string="Approve By", tracking=True, )
    reject_by = fields.Many2one('res.users', string="Reject By", tracking=True, )
    employee_ids = fields.One2many('overtime.line',
                                      inverse_name='request_id', tracking=True)
    
    file_attachment=fields.Binary(string="File Attachment")
    file_attachment_name=fields.Char(string="Attachment")
    project_id=fields.Many2one('project.project',string="Project Name")
    type_of_work=fields.Char(string="Type Of Work")
    total_time=fields.Float(string="Total Time")

    @api.constrains('employee_ids', 'total_time')
    def _check_total_hours(self):
        for record in self:
            total_employee_hours = sum(line.hours for line in record.employee_ids)
            if total_employee_hours > record.total_time:
                raise ValidationError(
                    f"Total employee overtime hours ({total_employee_hours:.2f}) "
                    f"cannot exceed the allowed total time ({record.total_time:.2f})."
                )

    @api.constrains('start_date', 'end_date')
    def _check_dates_not_in_past(self):
        for record in self:
            now = fields.Datetime.now()
            if record.start_date and record.start_date < now:
                raise ValidationError("Start Date cannot be in the past.")
            if record.end_date and record.end_date < now:
                raise ValidationError("End Date cannot be in the past.")

    def action_submit(self):
        for rec in self:
            rec.state="submit"
    def action_review(self):
        for rec in self:
            rec.state="review"
            rec.review_by=self.env.user.id
    def action_approve(self):
        for rec in self:
            rec.state = "approve"
            rec.approve_by = self.env.user.id
    def action_reject(self):
        for rec in self:
            rec.state = "reject"
            rec.reject_by = self.env.user.id


class OvertimeRequestEmployee(models.Model):
    _name = 'overtime.line'
    request_id = fields.Many2one('overtime.request', string="Request")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    start_date = fields.Datetime(string="Start Date", tracking=True, )
    end_date = fields.Datetime(string="End Date", tracking=True, )
    hours = fields.Float(string="Hours", tracking=True, compute="_compute_hours",store=True)
    remark = fields.Char(string="Remark", tracking=True, )

    @api.depends('start_date', 'end_date')
    def _compute_hours(self):
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.hours = delta.total_seconds() / 3600  # Convert seconds to hours
            else:
                record.hours = 0.0  # Set to 0 if dates are not set




