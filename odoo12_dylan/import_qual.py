'name:name',
'type:type_id',
'id_no: us_id',
'title : title',
'level1 : pre_nqf_level',
'level2 : nqf_level',
'level3 : credits',
'type_key : type_key',
'is_seta_approved : is_seta_approved',
'is_provider_approved : is_provider_approved',

line_id = fields.Many2one('provider.qualification', 'Order Reference', required=True, ondelete='cascade')
unit_standards_id = fields.Many2one('learner.assessment.line', string='Unit Standards')
unit_standards_verify_id = fields.Many2one('learner.assessment.verify.line', string='Unit Standards')
unit_standards_achieve_id = fields.Many2one('learner.assessment.achieve.line', string='Unit Standards')
unit_standards_achieved_id = fields.Many2one('learner.assessment.achieved.line', string='Unit Standards')
is_seta_approved = is_seta_approved
is_provider_approved = is_provider_approved




	qualification_ids = fields.Many2many(
		comodel_name='master.qualification',
		relation='qualification_us_rel',
		column1='unit_standard_id',
		column2='qualification_id',
		string='Qualification')
	skills_programme_ids = fields.Many2many(
		comodel_name='master.skills.programme',
		relation='skills_programme_us_rel',
		column1='unit_standard_id',
		column2='skills_programme_id',
		string='Skills Programme')

	learning_programme_ids = fields.Many2many(
		comodel_name='master.learning.programme',
		relation='learning_programme_us_rel',
		column1='unit_standard_id',
		column2='learning_programme_id',
		string='Learning Programme')
