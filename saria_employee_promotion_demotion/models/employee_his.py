from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
  

    promotion_count = fields.Integer('Promotion Count', compute='_compute_promotion_count')
    demotion_count = fields.Integer('Demotion Count', compute='_compute_demotion_count')

    @api.depends('promotion_count')
    def _compute_promotion_count(self):
        for employee in self:
            emp_pro=self.env['employee.promotion'].search([
                    ('employee_id','=',employee.id),
                    ('state','=','approve')
            ])
            employee.promotion_count = len(emp_pro)

    @api.depends('demotion_count')
    def _compute_demotion_count(self):
        for employee in self:
            emp_dmo=self.env['employee.demotion'].search([
                    ('employee_id','=',employee.id),
                    ('state','=','approve')
            ])
            employee.demotion_count = len(emp_dmo)


    def action_view_promotions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Promotions',
            'res_model': 'employee.promotion',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
            'target': 'current',
        }

    def action_view_demotions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Demotions',
            'res_model': 'employee.demotion',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
            'target': 'current',
        }