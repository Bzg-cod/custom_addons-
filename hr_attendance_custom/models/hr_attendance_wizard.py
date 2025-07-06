from odoo import models, fields, api,_
from datetime import timedelta, datetime
import calendar
from odoo.exceptions import UserError
from zk import ZK
import pytz
import logging
_logger = logging.getLogger(__name__)

class HrAttendanceWizardLine(models.Model):
    _name = "hr.attendance.wizard.line"
    _description = "Temporary Attendance Record"

    wizard_id = fields.Many2one('hr.attendance.wizard', string="Wizard Reference", required=True, ondelete="cascade")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    check_in = fields.Datetime(string="Check In", required=True)
    check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)
    day_name = fields.Char(string="Day Name")
    generated = fields.Boolean(default=False, related="wizard_id.attendance_generated")

    def action_move(self):
        """Create hr.attendance records from selected hr.attendance.wizard.line records"""
        attendance_model = self.env["hr.attendance"]

        for record in self:
            # Check if an hr.attendance record already exists for this employee and check_in/check_out
            existing_attendance = attendance_model.search([
                ('employee_id', '=', record.employee_id.id),
                ('check_in', '=', record.check_in),
                '|',  # Use OR condition to check either check_in or check_out
                ('check_out', '=', record.check_out),
                ('check_out', '=', False),  # Include records with no check_out
            ], limit=1)

            # Create hr.attendance only if no duplicate exists
            if not existing_attendance:
                attendance_vals = {
                    'employee_id': record.employee_id.id,
                    'check_in': record.check_in,
                }
                if record.check_out:  # Only add check_out if it exists
                    attendance_vals['check_out'] = record.check_out

                attendance_model.create(attendance_vals)

        # Optionally mark the wizard as generated
        if self.wizard_id:
            self.wizard_id.write({'attendance_generated': True})

        # Return action to close the wizard or refresh the view
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Attendance records created successfully!',
                'type': 'success',
            }
        }



    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0
            else:
                attendance.worked_hours = False


class HRAttendanceWizard(models.Model):
    _name = "hr.attendance.wizard"
    _description = "Employee Attendance Wizard"

    name = fields.Char(string="Allocation Name")
    data_from=state=fields.Selection([
        ('from_system',"From System"),
        ('from_machine',"From Machine"),
    ],required=True)
    department_ids = fields.Many2many('hr.department', string="Departments")
    employee_ids = fields.Many2many("hr.employee", string="Employees")
    date_from = fields.Date(string='Data From')
    date_to = fields.Date("End Date", required=True)
    attendance_lines = fields.One2many('hr.attendance.wizard.line', 'wizard_id', string="Generated Attendances")
    attendance_generated = fields.Boolean(default=False)

    state=fields.Selection([
        ('draft',"Draft"),
        ('generated',"Generated"),
    ],default='draft')

    @api.model
    def create(self, vals):
        if not vals.get('department_ids') and not vals.get('employee_ids'):
            vals['employee_ids'] = [(6, 0, self.env['hr.employee'].search([]).ids)]
        return super().create(vals)

    @api.onchange('department_ids', 'date_from', 'date_to')
    def _onchange_department_ids(self):
        """Populate employee_ids based on the selected departments or all employees if no department selected."""
        if self.department_ids:
            employees = self.env['hr.employee'].search([('department_id', 'in', self.department_ids.ids)])
            if employees:
                self.employee_ids = [(6, 0, employees.ids)]
            else:
                self.employee_ids = [(5, 0, 0)]
        else:
            # When no departments selected, include all employees
            employees = self.env['hr.employee'].search([])
            if employees:
                self.employee_ids = [(6, 0, employees.ids)]
            else:
                self.employee_ids = [(5, 0, 0)]

    # def create_attendance_records(self):
    #     """Creates real attendance records from the draft lines."""
    #     attendance_model = self.env["hr.attendance"]
    #     for line in self.attendance_lines:
    #         attendance_model.create({
    #             'employee_id': line.employee_id.id,
    #             'check_in': line.check_in,
    #             'check_out': line.check_out,
    #         })
    #     self.state='moved'

    def generate_draft_attendance(self):
        """Generates draft attendance records using employee working hours from resource.calendar.attendance."""
        try:
            self.ensure_one()
            attendance_line_model = self.env["hr.attendance.wizard.line"]

            # Clear previous draft records
            self.attendance_lines.unlink()

            # Use all employees if none specified
            employees = self.employee_ids if self.employee_ids else self.env['hr.employee'].search([])

            for employee in employees:
                contract = employee.contract_id
                if not contract or not contract.resource_calendar_id:
                    raise UserError(f'No contract found for employee: {employee.name}')

                work_schedule = contract.resource_calendar_id

                current_date = self.date_from
                while current_date <= self.date_to:
                    weekday = current_date.weekday()
                    day_name = calendar.day_name[weekday]

                    attendance = work_schedule.attendance_ids.filtered(lambda a: int(a.dayofweek) == weekday)

                    if not attendance:
                        current_date += timedelta(days=1)
                        continue

                    for att in attendance:
                        check_in_time = f"{int(att.hour_from)}:{int((att.hour_from % 1) * 60):02d}:00"
                        check_out_time = f"{int(att.hour_to)}:{int((att.hour_to % 1) * 60):02d}:00"

                        check_in = datetime.combine(current_date, datetime.strptime(check_in_time, "%H:%M:%S").time())
                        check_out = datetime.combine(current_date, datetime.strptime(check_out_time, "%H:%M:%S").time())

                        attendance_line_model.create({
                            'wizard_id': self.id,
                            'employee_id': employee.id,
                            'check_in': check_in,
                            'check_out': check_out,
                            'day_name': day_name,
                        })

                    current_date += timedelta(days=1)
                self.attendance_generated = True
                self.state='generated'
        except Exception as e:
            raise UserError(str(e))

    def create_draft_records(self):
        """Generate attendance records for selected employees or all employees if none selected within the given date range."""
        attendance_model = self.env["hr.attendance"]

        # Use all employees if none specified
        employees = self.employee_ids if self.employee_ids else self.env['hr.employee'].search([])

        for employee in employees:
            current_date = self.date_from
            while current_date <= self.date_to:
                existing_attendance = attendance_model.search([
                    ('employee_id', '=', employee.id),
                    ('check_in', '>=', current_date),
                    ('check_in', '<', current_date + timedelta(days=1))
                ])

                if not existing_attendance:
                    attendance_model.create({
                        'employee_id': employee.id,
                        'check_in': current_date.strftime('%Y-%m-%d 08:00:00'),
                        'check_out': current_date.strftime('%Y-%m-%d 17:00:00'),
                    })
                current_date += timedelta(days=1)

        return {'type': 'ir.actions.act_window_close'}
    
    def generate_attendance_from_machine(self):
        """Fetch attendance data from biometric devices and store it in hr.attendance.wizard.line"""
        biometric_devices = self.env['biometric.device.details'].search([])  # Fetch all devices

        if not biometric_devices:
            raise UserError(_("No biometric devices found. Please configure devices in 'Biometric Device Details'."))

        # Clear existing lines
        self.attendance_lines.unlink()

        for device in biometric_devices:
            machine_ip = device.device_ip
            zk_port = device.port_number

            # Test connection to the device
            try:
                zk = ZK(machine_ip, port=zk_port, timeout=15, password=0, force_udp=False, ommit_ping=False)
            except NameError:
                raise UserError(
                    _("Pyzk module not found. Please install it with 'pip3 install pyzk'."))

            conn = device.device_connect(zk)
            if not conn:
                _logger.info(f"Skipping device {machine_ip}:{zk_port} - Unable to connect.")
                continue  # Skip to the next device if connection fails

            try:
                conn.disable_device()  # Disable device during data fetch
                attendance = conn.get_attendance()
                users = conn.get_users()

                if not attendance:
                    _logger.info(f"No attendance data found for device {machine_ip}.")
                    continue

                # Convert date_from and date_to to datetime for comparison
                date_from = datetime.combine(self.date_from, datetime.min.time())
                date_to = datetime.combine(self.date_to, datetime.max.time())
                local_tz = pytz.timezone(self.env.user.partner_id.tz or 'GMT')

                for each in attendance:
                    atten_time = each.timestamp

                    # Filter attendance by date range
                    if not (date_from <= atten_time <= date_to):
                        continue

                    # Convert to UTC and format
                    local_dt = local_tz.localize(atten_time, is_dst=None)
                    utc_dt = local_dt.astimezone(pytz.utc)
                    atten_time_str = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                    atten_time = fields.Datetime.to_string(
                        datetime.strptime(atten_time_str, "%Y-%m-%d %H:%M:%S"))

                    # Match user from device to employee
                    employee = None
                    for uid in users:
                        if uid.user_id == each.user_id:
                            employee = self.env['hr.employee'].search(
                                [('device_id_num', '=', each.user_id)], limit=1)
                            if not employee:
                                continue

                    if employee and (not self.employee_id or employee.id == self.employee_id.id):
                        # Define search criteria based on punch type
                        search_domain = [
                            ('wizard_id', '=', self.id),
                            ('employee_id', '=', employee.id),
                        ]
                        if each.punch == 0:  # Check-in
                            search_domain.append(('check_in', '=', atten_time))
                        elif each.punch == 1:  # Check-out
                            search_domain.append(('check_out', '=', atten_time))

                        # Search for existing record
                        existing_record = self.env['hr.attendance.wizard.line'].search(search_domain, limit=1)

                        # Create record only if it doesn't exist
                        if not existing_record:
                            self.env['hr.attendance.wizard.line'].create({
                                'wizard_id': self.id,
                                'employee_id': employee.id,
                                'check_in': atten_time if each.punch == 0 else False,
                                'check_out': atten_time if each.punch == 1 else False,
                                'day_name': atten_time.strftime('%A') if atten_time else False,
                            })

                conn.enable_device()  # Re-enable device
                conn.disconnect()


            except Exception as e:
                _logger.error(f"Error fetching data from {machine_ip}: {str(e)}")
                conn.enable_device()
                conn.disconnect()
                continue

        # Return action to refresh the wizard form
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.attendance.approval.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }