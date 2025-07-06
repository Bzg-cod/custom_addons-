from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    demotion_ids = fields.One2many('employee.demotion', 'employee_id', string='Demotion')
    old_job_id = fields.Many2one('hr.job', related='contract_id.job_id', string='Previous Job Position', readonly=True)
    old_wage = fields.Float('Previous Salary', readonly=True, compute='_compute_old_wage')
    current_job_id = fields.Many2one('hr.job', string='Current Job Position', compute='_compute_current_job_id', store=True)
    current_wage = fields.Float('Current Salary', compute='_compute_current_wage', store=True)

    @api.depends('contract_ids', 'contract_ids.job_id')
    def _compute_current_job_id(self):
        for employee in self:
            contract = employee.contract_ids.sorted(key=lambda r: r.date_start, reverse=True)[:1]
            employee.current_job_id = contract.job_id if contract else False

    @api.depends('contract_ids', 'contract_ids.wage')
    def _compute_old_wage(self):
        for employee in self:
            contracts = employee.contract_ids.sorted(key=lambda r: r.date_start, reverse=True)
            # Use the second most recent contract (if exists) for old_wage
            employee.old_wage = contracts[1].wage if len(contracts) > 1 else 0.0

    @api.depends('contract_ids', 'contract_ids.wage')
    def _compute_current_wage(self):
        for employee in self:
            contract = employee.contract_ids.sorted(key=lambda r: r.date_start, reverse=True)[:1]
            employee.current_wage = contract.wage if contract else 0.0


class EmployeeDemotion(models.Model):
    _name = 'employee.demotion'
    _description = 'Employee Demotion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    old_job = fields.Char('Previous Job Position', readonly=True)
    old_job_id = fields.Many2one('hr.job', string='Previous Job Position')
    old_salary = fields.Float('Previous Salary')
    demotion_date = fields.Date('Demotion Date', default=fields.Date.today())
    new_job_id = fields.Many2one('hr.job', string='New Job Position')
    new_wage = fields.Float('New Salary')
    
    # Old Allowance Fields (aligned with hr.contract)
    old_transportation_allowance = fields.Float('Transportation Allowance')
    old_position_allowance = fields.Float('Position Allowance')
    old_fuel_allowance = fields.Float('Fuel Allowance')
    old_food_allowance = fields.Float('Food Allowance')  # Renamed from meal_allowance
    old_other_allowance = fields.Float('Other Allowance')
    old_inflation_adjustment = fields.Float('Inflation Adjustment')
    old_communication_allowance = fields.Float('Communication Allowance')
    old_internet_allowance = fields.Float('Internet Allowance')
    old_unused_leave_payment = fields.Float('Unused Leave Payment')
    old_severance_pay_compensation = fields.Float('Severance Pay Compensation')  # Fixed typo
    old_training_development = fields.Float('Training Development')
    old_desert_allowance = fields.Float('Desert Allowance')
    old_representation_allowance = fields.Float('Representation Allowance')

    # New Allowance Fields (aligned with hr.contract)
    new_transportation_allowance = fields.Float('Transportation Allowance')
    new_position_allowance = fields.Float('Position Allowance')
    new_fuel_allowance = fields.Float('Fuel Allowance')
    new_food_allowance = fields.Float('Food Allowance')  # Renamed from meal_allowance
    new_other_allowance = fields.Float('Other Allowance')
    new_inflation_adjustment = fields.Float('Inflation Adjustment')
    new_communication_allowance = fields.Float('Communication Allowance')
    new_internet_allowance = fields.Float('Internet Allowance')
    new_unused_leave_payment = fields.Float('Unused Leave Payment')
    new_severance_pay_compensation = fields.Float('Severance Pay Compensation')  # Fixed typo
    new_training_development = fields.Float('Training Development')
    new_desert_allowance = fields.Float('Desert Allowance')
    new_representation_allowance = fields.Float('Representation Allowance')
    reason=fields.Text(string="Reason")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approve', 'Approved')],
        default="draft")

    def action_submit(self):
        self.state = 'submit'

    @api.model
    def create(self, vals):
        employee_id = vals['employee_id']
        contract = self.env['hr.contract'].search(
            ['&', ('employee_id', '=', employee_id), ('state', '=', 'open')])
        record = super(EmployeeDemotion, self).create(vals)

        if contract:
            record.old_salary = contract.wage
            if contract.job_id:
                record.old_job = contract.job_id.name
                record.old_job_id = contract.job_id.id
            record.old_transportation_allowance = contract.transportation_allowance
            record.old_position_allowance = contract.position_allowance
            record.old_fuel_allowance = contract.fuel_allowance
            record.old_food_allowance = contract.food_allowance  # Updated
            record.old_other_allowance = contract.other_allowance
            record.old_inflation_adjustment = contract.inflation_adjustment
            record.old_communication_allowance = contract.communication_allowance
            record.old_internet_allowance = contract.internet_allowance
            record.old_unused_leave_payment = contract.unused_leave_payment
            record.old_severance_pay_compensation = contract.severance_pay_compensation  # Fixed typo
            record.old_training_development = contract.training_development
            record.old_desert_allowance = contract.desert_allowance
            record.old_representation_allowance = contract.representation_allowance

            # Set new values to old values by default
            record.new_wage = contract.wage
            record.new_transportation_allowance = contract.transportation_allowance
            record.new_position_allowance = contract.position_allowance
            record.new_fuel_allowance = contract.fuel_allowance
            record.new_food_allowance = contract.food_allowance
            record.new_other_allowance = contract.other_allowance
            record.new_inflation_adjustment = contract.inflation_adjustment
            record.new_communication_allowance = contract.communication_allowance
            record.new_internet_allowance = contract.internet_allowance
            record.new_unused_leave_payment = contract.unused_leave_payment
            record.new_severance_pay_compensation = contract.severance_pay_compensation
            record.new_training_development = contract.training_development
            record.new_desert_allowance = contract.desert_allowance
            record.new_representation_allowance = contract.representation_allowance

        return record

    @api.onchange('employee_id')
    def _compute_old_salary(self):
        for employee in self:
            contract = self.env['hr.contract'].search(
                ['&', ('employee_id', '=', employee.employee_id.id), ('state', '=', 'open')])
            if contract:
                employee.old_salary = contract.wage
                if contract.job_id:
                    employee.old_job = contract.job_id.name
                    employee.old_job_id = contract.job_id.id
                employee.old_transportation_allowance = contract.transportation_allowance
                employee.old_position_allowance = contract.position_allowance
                employee.old_fuel_allowance = contract.fuel_allowance
                employee.old_food_allowance = contract.food_allowance
                employee.old_other_allowance = contract.other_allowance
                employee.old_inflation_adjustment = contract.inflation_adjustment
                employee.old_communication_allowance = contract.communication_allowance
                employee.old_internet_allowance = contract.internet_allowance
                employee.old_unused_leave_payment = contract.unused_leave_payment
                employee.old_severance_pay_compensation = contract.severance_pay_compensation
                employee.old_training_development = contract.training_development
                employee.old_desert_allowance = contract.desert_allowance
                employee.old_representation_allowance = contract.representation_allowance

                # Set new values to old values by default
                employee.new_wage = contract.wage
                employee.new_transportation_allowance = contract.transportation_allowance
                employee.new_position_allowance = contract.position_allowance
                employee.new_fuel_allowance = contract.fuel_allowance
                employee.new_food_allowance = contract.food_allowance
                employee.new_other_allowance = contract.other_allowance
                employee.new_inflation_adjustment = contract.inflation_adjustment
                employee.new_communication_allowance = contract.communication_allowance
                employee.new_internet_allowance = contract.internet_allowance
                employee.new_unused_leave_payment = contract.unused_leave_payment
                employee.new_severance_pay_compensation = contract.severance_pay_compensation
                employee.new_training_development = contract.training_development
                employee.new_desert_allowance = contract.desert_allowance
                employee.new_representation_allowance = contract.representation_allowance
            else:
                employee.old_salary = 0.0

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)], limit=1, order='date_start desc')
            self.old_job_id = contract.job_id.id if contract else False

    @api.model
    def _update_employee_job_salary(self, demotion):
        update = self.env['hr.contract'].search(
            ['&', ('employee_id', '=', demotion.employee_id.id), ('state', '=', 'open')])
        update.write({
            'job_id': demotion.new_job_id.id,
            'wage': demotion.new_wage,
            'transportation_allowance': demotion.new_transportation_allowance,
            'position_allowance': demotion.new_position_allowance,
            'fuel_allowance': demotion.new_fuel_allowance,
            'food_allowance': demotion.new_food_allowance,
            'other_allowance': demotion.new_other_allowance,
            'inflation_adjustment': demotion.new_inflation_adjustment,
            'communication_allowance': demotion.new_communication_allowance,
            'internet_allowance': demotion.new_internet_allowance,
            'unused_leave_payment': demotion.new_unused_leave_payment,
            'severance_pay_compensation': demotion.new_severance_pay_compensation,
            'training_development': demotion.new_training_development,
            'desert_allowance': demotion.new_desert_allowance,
            'representation_allowance': demotion.new_representation_allowance,
        })

    def action_approve(self):
        for demotion in self:
            self.state = 'approve'
            demotion._update_employee_job_salary(demotion)