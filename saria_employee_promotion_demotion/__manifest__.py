{
    'name': 'Employee Promotion',
    'version': '17.0.0.1',
    
    'category': 'Human Resources',
    'summary': 'Track employee promotions',
    'author': 'Tamrat',

    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
       'security/group.xml',

        'views/employee_promotion.xml',
        'views/hr_employee_views.xml',
        'views/employee_demotion.xml',

    ],
    'installable': True,
    'application': True,
}
