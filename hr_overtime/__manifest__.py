{
    'name': 'HR Overtime',
    'version': '17.0.0.1',
    'summary': 'HR Overtime',
    'description': """HR Overtime""",
    'category': '',
    'website': '',
    'depends': [
        'hr',
        'base',
        'base_setup',
        'hr_contract',
        'om_hr_payroll',
        'hr_work_entry_holidays',
        'project'
    ],

    'license': 'LGPL-3',

    'data': [
        'security/ir.model.access.csv',
        'security/overtime_approver_group.xml',
        'data/data.xml',
        'data/overtime_request_notification.xml',
        'views/overtime_calculation.xml',
        'views/overtime_rate.xml',
        'views/overtime_request.xml',
        'views/custom_hr_attendance.xml',
    ],
    'assets': {},
    'installable': True,
    'application': False,
}
