{
    'name': 'Payroll Dynamic Report',
    'version': '1.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Dynamic payroll reporting with PDF and XLSX export',
    'depends': ['om_hr_payroll','hr'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/payroll_report_wizard_views.xml',
        # 'report/payroll_report_templates.xml',
        'views/hr_employee.xml',
    ],
    'installable': True,
    'application': False,
}