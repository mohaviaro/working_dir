# from pygments.lexer import _inherit

from odoo import api, fields, models, _
from odoo.api import onchange
from odoo.exceptions import UserError
from odoo.models import AccessError
import datetime as dt, re
from . import validations_ds as vd
from . import validations_ds as vds
from . import validation_fields as vf
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.tools import pycompat
import datetime
import pytz
from odoo.addons.base.models.res_partner import _tz_get
from odooly import Client
import pdb
# import wdb
v8_mode = "live"
DEBUG = True

if DEBUG:
	import logging

	logger = logging.getLogger(__name__)

	def dbg(*args):
		msg = ''.join([str(arg) for arg in args])
		logger.info(msg)
else:
	def dbg(msg):
		pass

class organizationMeta(models.Model):
	_name = 'organization.meta'
	_inherit = ['res.partner', 'mail.thread', 'mail.activity.mixin']
	_description = "Non levy paying Organization"

	page = fields.Selection([
		('step1', 'Org Details'),
		('step2', 'Documents Upload'),
		('step5', 'Banking Details'),
		# ('provider', 'Provider'),

	], default='step1')

	_sql_constraints = [
		('ref', 'unique (ref)', "The Internal Reference number is in use. Please use another one"),
	]

	is_employer = fields.Boolean(string="Organization", default=True)
	emp_government = fields.Boolean('Government')
	emp_levy_paying = fields.Boolean('Levy Paying')
	emp_university = fields.Boolean('University (CHE)')
	emp_non_levy_paying = fields.Boolean('Non Levy Paying')
	emp_tvet_college = fields.Boolean('TVET College (DHET)')
	emp_exempt = fields.Boolean('Levy Exempt')
	emp_other_group = fields.Boolean('Other')
	emp_ngo_npo = fields.Boolean('NGO/NPO')
	emp_cbo = fields.Boolean('CBO')
	emp_fbo = fields.Boolean('FBO')
	emp_section = fields.Boolean('Section 21')
	emp_other_group_info = fields.Char(size=70)
	emp_health = fields.Boolean('Health')
	emp_walfare = fields.Boolean('Welfare')
	emp_other = fields.Boolean('Other')
	emp_other_info = fields.Char(size=70)
	mand_grant_banking_details = fields.Many2one('ir.attachment', 'Mandatory Grant Banking Details')
	disc_grant_banking_details = fields.Many2one('ir.attachment', 'Discretionary Grant Banking Details')
	levy_exempt_certificate = fields.Many2one('ir.attachment', string='Levy Exempt Certificate')
	npo_certificate = fields.Many2one('ir.attachment', string='NPO Certificate ')
	bbee_certificate = fields.Many2one('ir.attachment', string='B-BEE Certificate')
	transaction_type = fields.Selection([('new', 'New'), ('updated', 'Updated')],
							 default='new')

	##FIELDS TO ADD
	# emp_reg_number_type = fields.Char()
	name = fields.Char(string="Name")
	vendor = fields.Char(string="Vendor")
	employer_registration_number = fields.Char(string="Registration Number")
	employer_vat_number = fields.Char(string="Vat Number")
	site_no = fields.Char()
	state = fields.Selection([
		('draft', 'Draft'),
		('sdp_submitted', 'SDP Submitted'),
		('sdp_approved', 'SDP Approved'),
		('submitted', 'Finance Submitted'),
		('approved', 'Approved'),
		('rejected', 'Rejected'),
	], readonly=True, default='draft', string='State')
	submitted = fields.Boolean(string='Completely Submitted')
	approved = fields.Boolean(string='Approved')
	sdp_approved = fields.Boolean(string='SDP Approved')
	sdp_submit = fields.Boolean(string='SDP Submission')
	fin_submit = fields.Boolean(string='Finance Submission')
	rejected = fields.Boolean(string='Rejected')
	comments = fields.Text(string='Comments')
	alt_sdl_prefix = fields.Selection([('prefix_N', 'N'), ('prefix_g', 'G'), ('prefix_T', 'T'), ('prefix_L', 'L')], size=10,
									  string='SDL number prefix')

	prefix_N = fields.Char(string='N')
	prefix_L = fields.Char(string='L')
	prefix_g = fields.Char(string='G')
	prefix_T = fields.Char(string='T')

	partner_id = fields.Many2one('res.partner', string='Name')
	person_title = fields.Selection(
		[('adv', 'Adv.'), ('dr', 'Dr'), ('mr', 'Mr'), ('mrs', 'Mrs'), ('ms', 'Ms'), ('prof', 'Prof')], string='Title',
		track_visibility='onchange')

	django_id = fields.Integer()
	mandatory_account = fields.Many2one('organization.bank.account')
	discretionary_account = fields.Many2one('organization.bank.account')
	employer_company_name = fields.Char(size=70, required=False)
	imported_updated_flg = fields.Boolean()
	record_updated_flg = fields.Boolean()

	bank_ids = fields.One2many('organization.bank.account', 'org_meta_id', string='Banks')

	property_account_payable_id = fields.Many2one('account.account', string="Account Payable", default=486)
	property_account_receivable_id = fields.Many2one('account.account', string="Account Recevable", default=509)

	vfields = vf.sf
	employer_dict_overload = vfields['seta.employer']['fields']
	employer_site_no = fields.Char(size=10)

##############################
#######Validations############
##############################
	# person_home_address_1
	@api.onchange("person_home_address_1")
	def onchange_person_home_address_1_validations(self):
		dbg("def onchange_person_home_address_1_validations(self):")
		field_name = 'Home Address 1'
		if self.person_home_address_1:
			self.person_home_address_1 = self.person_home_address_1.stip()
			broken, msg = vds.check_person_home_address_1(self.person_home_address_1)
			if broken:
				return {'warning': {'title': 'Invalid ' + field_name,
									'message': msg + '\nPlease re-enter a valid ' + field_name},
						'value': {'person_home_address_1': False}}
			# raise ValidationError(_(msg))
		value = str(self.person_home_address_1)
		repl_value = value.replace(" ", "")
		num_value = repl_value.isnumeric()
		if num_value and self.person_home_address_1:
			return {'warning': {'title': 'Invalid ' + field_name,
								'message': field_name + ' may not contain only numbers' + '\nPlease re-enter a valid ' + field_name},
					'value': {'person_home_address_1': False}}


	# person_home_address_2
	@api.onchange("person_home_address_2")
	def onchange_person_home_address_2_validations(self):
		dbg("def onchange_person_home_address_2_validations(self):")
		field_name = 'Home Address 2'
		if self.person_home_address_2:
			self.person_home_address_2 = self.person_home_address_2.strip()
			broken, msg = vds.check_person_home_address_2(self.person_home_address_2)
			if broken:
				return {'warning': {'title': 'Invalid ' + field_name,
									'message': msg + '\nPlease re-enter a valid ' + field_name},
						'value': {'person_home_address_2': False}}
			# raise ValidationError(_(msg))
		value = str(self.person_home_address_2)
		repl_value = value.replace(" ", "")
		num_value = repl_value.isnumeric()
		if num_value and self.person_home_address_2:
			return {'warning': {'title': 'Invalid ' + field_name,
								'message': field_name + ' may not contain only numbers' + '\nPlease re-enter a valid ' + field_name},
					'value': {'person_home_address_2': False}}

	# person_home_address_3
	@api.onchange("person_home_address_3")
	def onchange_person_home_address_3_validations(self):
		dbg("def onchange_person_home_address_3_validations(self):")
		field_name = 'Home Address 3'
		if self.person_home_address_3:
			self.person_home_address_3 = self.person_home_address_3.strip()
			broken, msg = vds.check_person_home_address_3(self.person_home_address_3)
			if broken:
				return {'warning': {'title': 'Invalid ' + field_name,
									'message': msg + '\nPlease re-enter a valid ' + field_name},
						'value': {'person_home_address_3': False}}
			# raise ValidationError(_(msg))
		value = str(self.person_home_address_3)
		repl_value = value.replace(" ", "")
		num_value = repl_value.isnumeric()
		check = r"(0123|1234|2345|3456|4567|5678|6789|3210|4321|5432|6543|7654|8765|9876|0000|1111|2222|3333|4444|5555|6666|7777|8888|9999)"
		is_consecutive_num = bool(re.findall(check, value))
		if self.person_home_address_3 and is_consecutive_num == True:
			return {'warning': {'title': 'Invalid ' + field_name,
								'message': field_name + ' may not contain 4 consecutive numbers' + '\nPlease re-enter a valid ' + field_name},
					'value': {'person_home_address_3': False}}
		if num_value and self.person_home_address_3:
			return {'warning': {'title': 'Invalid ' + field_name,
								'message': field_name + ' may not contain only numbers' + '\nPlease re-enter a valid ' + field_name},
					'value': {'person_home_address_3': False}}

	# Postal_code
	@api.onchange("person_home_zip")
	def onchange_person_address_code_validations(self):
		dbg("def onchange_person_address_code_validations(self):")
		field_name = 'ZIP Code'
		if self.person_home_zip:
			broken, msg = vds.check_person_address_code(self.person_home_zip)
			if broken:
				return {'warning': {'title': 'Invalid ' + field_name,
									'message':'\nPlease re-enter a valid ' + field_name},
						'value': {'person_home_zip': False}}

	# person_postal_address_1
	@api.onchange("person_postal_address_1")
	def onchange_person_postal_address_1_validations(self):
		dbg("def onchange_person_postal_address_1_validations(self):")
		field_name = 'Postal Address 1'
		if self.person_postal_address_1:
			self.person_postal_address_1 = self.person_postal_address_1.strip()
			broken, msg = vds.check_person_postal_address_1(
				self.person_postal_address_1
			)
			if broken:
				return {'warning': {'title': 'Invalid ' + field_name,
									'message': msg + '\nPlease re-enter a valid ' + field_name},
						'value': {'person_postal_address_1': False}}

		value = str(self.person_postal_address_1)
		repl_value = value.replace(" ", "")
		num_value = repl_value.isnumeric()
		if num_value and self.person_postal_address_1:
			return {'warning': {'title': 'Invalid ' + field_name,
								'message': field_name + ' may not contain only numbers' + '\nPlease re-enter a valid ' + field_name},
					'value': {'person_postal_address_1': False}}

	# person_postal_address_2
	@api.onchange("person_postal_address_2")
	def onchange_person_postal_address_2_validations(self):
		field_name = 'Postal Address 2'
		dbg("def onchange_person_postal_address_2_validations(self):")
		if self.person_postal_address_2:
			self.person_postal_address_2 = self.person_postal_address_2.strip()
			broken, msg = vds.check_person_postal_address_2(
				self.person_postal_address_2
			)
			if broken:
				return {'warning': {'title': 'Invalid ' + field_name,
									'message': msg + '\nPlease re-enter a valid ' + field_name},
						'value': {'person_postal_address_2': False}}

		value = str(self.person_postal_address_2)
		repl_value = value.replace(" ", "")
		num_value = repl_value.isnumeric()
		if num_value and self.person_postal_address_2:
			return {'warning': {'title': 'Invalid ' + field_name,
								'message': field_name + ' may not contain only numbers' + '\nPlease re-enter a valid ' + field_name},
					'value': {'person_postal_address_2': False}}

	# person_postal_address_3
	@api.onchange("person_postal_address_3")
	def onchange_person_postal_address_3_validations(self):
		dbg("def onchange_person_postal_address_3_validations(self):")
		field_name = 'Postal Address 3'
		if self.person_postal_address_3:
			self.person_postal_address_3 = self.person_postal_address_3.strip()
			broken, msg = vds.check_person_postal_address_3(
				self.person_postal_address_3
			)
			if broken:
				return {'warning': {'title': 'Invalid ' + field_name,
									'message': msg + '\nPlease re-enter a valid ' + field_name},
						'value': {'person_postal_address_3': False}}

		value = str(self.person_postal_address_3)
		repl_value = value.replace(" ", "")
		num_value = repl_value.isnumeric()
		check = r"(0123|1234|2345|3456|4567|5678|6789|3210|4321|5432|6543|7654|8765|9876|0000|1111|2222|3333|4444|5555|6666|7777|8888|9999)"
		is_consecutive_num = bool(re.findall(check, value))
		if self.person_postal_address_3 and is_consecutive_num == True:
			return {'warning': {'title': 'Invalid ' + field_name,
								'message': field_name + ' may not contain 4 consecutive numbers' + '\nPlease re-enter a valid ' + field_name},
					'value': {'person_postal_address_3': False}}
		if num_value and self.person_postal_address_3:
			return {'warning': {'title': 'Invalid ' + field_name,
								'message': field_name + ' may not contain only numbers' + '\nPlease re-enter a valid ' + field_name},
					'value': {'person_postal_address_3': False}}

	# person_postal_address_code
	@api.onchange("person_postal_zip")
	def onchange_person_postal_address_code_validations(self):
		dbg("def onchange_person_postal_address_code_validations(self):")
		field_name = 'ZIP Code'
		if self.person_postal_zip:
			broken, msg = vds.check_person_postal_address_code(
				self.person_postal_zip
			)
			if broken:
				return {'warning': {'title': 'Invalid ' + field_name,
									'message': '\nPlease re-enter a valid ' + field_name},
						'value': {'person_postal_zip': False}}

#Site_no
	@api.onchange("employer_site_no")
	def onchange_employer_site_no_validations(self):
		field_name = 'Site No'
		if self.employer_site_no:
			self.employer_site_no = self.employer_site_no.strip()
			broken, msg = vds.check_site_no(self.employer_site_no)
			if broken:
				return {'warning': {'title': 'Invalid ' + field_name,
									'message': msg + '\nPlease re-enter a valid ' + field_name},
						'value': {'employer_site_no': False}}

#employer_registration_number
	@api.onchange("employer_registration_number")
	def onchange_employer_registration_number_validations(self):
		field_name = 'Employer Registration Number'
		if self.employer_registration_number:
			self.employer_registration_number = self.employer_registration_number.strip()
			broken, msg = vds.check_employer_registration_number(self.employer_registration_number)
			if broken:
				return {'warning': {'title': 'Invalid ' + field_name,
									'message': msg + '\nPlease re-enter a valid ' + field_name},
						'value': {'employer_registration_number': False}}

#employer_trading_name
	@api.onchange("employer_trading_name")
	def onchange_employer_trading_name_validations(self):
		field_name = 'Trading as'
		if self.employer_trading_name:
			self.employer_trading_name = self.employer_trading_name.strip()
			broken, msg = vds.check_employer_trading_name(self.employer_trading_name)
			if broken:
				return {'warning': {'title': 'Invalid ' + field_name,
									'message': msg + '\nPlease re-enter a valid ' + field_name},
						'value': {'employer_trading_name': False}}


	total_annual_payroll = fields.Float(string='Total Anual Payroll')
	employees_count = fields.Integer(string='Employees as per Employment Profile')
	organisation_size = fields.Selection(
		[('small', 'Small (0-49)'), ('medium', 'Medium (50-149)'), ('large', 'Large (150+)')],
		compute='_get_organisation_size', string='Organisation Size', readonly=True)

	@api.one
	@api.depends('employees_count')
	def _get_organisation_size(self):
		if self.employees_count <= 49:
			self.organisation_size = 'small'
		elif self.employees_count > 49 or self.employees_count <= 149:
			self.organisation_size = 'medium'
		else:
			self.organisation_size = 'large'

	def overload_employer(employer_dict_overload, name, validator):
		employer_dict_overload[name] = [validator]

	overload_employer(employer_dict_overload, "name", vd.check_employer_company_name)
	overload_employer(employer_dict_overload, "phone", vd.check_employer_phone_number)
	overload_employer(employer_dict_overload, "mobile", vd.check_employer_contact_cell_number)
	overload_employer(employer_dict_overload, "email", vd.check_employer_contact_email_address)
	overload_employer(employer_dict_overload, "website", vd.check_provider_website_address)
	overload_employer(employer_dict_overload, "street", vd.check_employer_physical_address_1)
	overload_employer(employer_dict_overload, "street2", vd.check_employer_physical_address_2)
	overload_employer(employer_dict_overload, "street3", vd.check_employer_physical_address_3)
	overload_employer(employer_dict_overload, "zip", vd.check_employer_physical_address_code)
	overload_employer(employer_dict_overload, "person_home_address_1", vd.check_employer_physical_address_1)
	overload_employer(employer_dict_overload, "person_home_address_2", vd.check_employer_physical_address_2)
	overload_employer(employer_dict_overload, "person_home_address_3", vd.check_employer_physical_address_3)
	overload_employer(employer_dict_overload, "person_home_zip", vd.check_employer_physical_address_code)
	overload_employer(employer_dict_overload, "person_postal_address_1", vd.check_employer_postal_address_1)
	overload_employer(employer_dict_overload, "person_postal_address_2", vd.check_employer_postal_address_2)
	overload_employer(employer_dict_overload, "person_postal_address_3", vd.check_employer_postal_address_3)
	overload_employer(employer_dict_overload, "person_postal_zip", vd.check_employer_postal_address_code)
	# overload_employer(employer_dict_overload, "employer_sdl_no", vd.check_sdl_no)
	overload_employer(employer_dict_overload, "employer_site_no", vd.check_site_no)

	def overload_logic(self, vals, is_onchange):
		if is_onchange == 1:
			looker = self
			mechanism = "raise"
		else:
			looker = vals
			mechanism = "append"
		final_msg = []
		data = []
		broken = []
		for k in self.employer_dict_overload.keys():
			validators = self.employer_dict_overload[k]
			for validator in validators:
				if k in looker:
					# dbg("field", k)
					try:
						data = validator(looker[k])
					except Exception as e:
						# dbg("field:", k, e)
						# employer_site no seems to be an outlier. validate manually
						dbg(looker)
						dbg(type(looker))
					# site no causing a break. commented out for now
					# if looker['employer_site_no']:
					# 	if not looker['employer_site_no'].isalnum():
					# 		data = [True, 'Employer Site No should only contain numbers and letters\n']
					# raise UserError(e)
					if data:
						broken = data[0]

					# index out of range on org imports
					if len(data) > 1:
						msg = data[1]
					if broken:
						if mechanism == 'append':
							final_msg.append(msg)
						elif mechanism == 'raise':
							raise UserError(msg)
		return final_msg

	@api.model
	def create(self, vals):
		#default entries
		if self.property_account_receivable_id:
			receivable = self.property_account_receivable_id
		else:
			receivable = 486
		if self.property_account_payable_id:
			payable = self.property_account_payable_id
		else:
			payable = 509

		vals.update({'property_account_receivable_id': receivable,
					 'property_account_payable_id':payable})
		final_msg = self.overload_logic(vals, 0)
		if len(final_msg) == 0:
			return super(organizationMeta, self).create(vals)  # pass
		else:
			raise UserError(''.join([str(m) + "\n" for m in final_msg]))

	# @api.model
	# def write(self, vals):
	#	final_msg = self.overload_logic(vals, 0)
	#	if len(final_msg) == 0:
	#		return super(organizationMeta, self).write(vals)  # pass
	#	else:
	#		raise UserError(''.join([str(m) + "\n" for m in final_msg]))
	#
	#	# @api.onchange('name','phone','mobile','email','website','street','street2','street3','zip','person_home_address_1','person_home_address_2', 'person_home_address_3', 'person_home_zip', 'person_postal_address_1', 'person_postal_address_2', 'person_postal_address_3', 'person_postal_zip', 'employer_sdl_no','employer_site_no')
	#	# def setmis_onchange_ds(self):
	#	#	  self.overload_logic(False, 1)

	def post_organization(self):
		pass

	def open_commercial_entity(self):
		pass

	@api.depends('is_company', 'parent_id.commercial_partner_id')
	def _compute_commercial_partner(self):
		# pass
		for partner in self.partner_id:
			if partner.is_company or not partner.parent_id:
				partner.commercial_partner_id = partner
			else:
				partner.commercial_partner_id = partner.parent_id.commercial_partner_id

	@api.multi
	def v8_log(self, name, create_or_update, approver, status, message):
		dbg('Log what happened')
		self.env['organization.meta.v8.log'].create({
			"name": name,
			"create_or_update": create_or_update,
			"approver_on_12": approver,
			"status": status,
			"message": message,
		})

	@api.multi
	def v8_all_children(self, v8, child_ids, parent_id):
		dbg('Check for children in v12, v8 and set the parent_id in v8:')
		dbg(parent_id)
		dbg(child_ids)
		r12 = self.env['res.partner'].browse(parent_id[0])
		sdl_12 = r12.employer_sdl_no
		if child_ids:
			for child in child_ids:
				c_r12 = self.env['res.partner'].browse(child)
				c_sdl_12 = c_r12.employer_sdl_no
				dbg(c_r12)
				c_r8 = v8.env['res.partner'].search([('employer_sdl_no','=',c_sdl_12)])
				try:
					c_r8.write({"parent_id": parent_id[0]})
				except Exception as e:
					dbg("Failed to update child ids"+ str(e))

	@api.multi
	def v8_create(self, v8, vals):
		vals = self.tuple_fixer([vals])
		vals = vals[0]
		vals['employer'] = True
		dbg('Did not detect the Org, going to create', v8)
		try:
			v8_res_partner = v8.env['res.partner']
			new_partner = v8_res_partner.create(vals)
			dbg(new_partner)
			self.v8_log(vals['name'], 'create', self.env.user.name, 'success', 'Successfully created')
		except Exception as e:
			self.v8_log(vals['name'], 'create', self.env.user.name, 'error', e)

	@api.multi
	def v8_update(self, v8, vals):
		dbg('V12TO Did detect the Org, going to update', v8)
		vals = self.tuple_fixer([vals])
		vals = vals[0]
		vals["employer"] = True
		dbg("V12TO" + str(vals['employer_sdl_no']))#raise UserError(existing_partner)
		v8_res_partner = v8.env['res.partner']
		dbg("V12TO" + str(v8_res_partner))#raise UserError(existing_partner)
		dbg("V12TO" + str(vals['employer_sdl_no']))#raise UserError(existing_partner)
		existing_partner = v8_res_partner.search([('employer_sdl_no','=',vals['employer_sdl_no'])])
		dbg("V12TO" + str(existing_partner))#raise UserError(existing_partner)
		if 'child_employer_ids' in vals:
			child_employer_ids = vals['child_employer_ids']
			del vals['child_employer_ids']
		else:
			child_ids = None
		dbg("V12TO" + str(vals))#raise UserError(existing_partner)
		existing_partner.write(vals)
		if child_employer_ids:
			self.v8_all_children(v8, child_employer_ids, existing_partner.id)
		try:
			self.v8_log(vals['name'], 'update', self.env.user.name, 'success', 'Successfully updated')
		except Exception as e:
			self.v8_log(vals['name'], 'update', self.env.user.name, 'error', e)

	@api.multi
	def import_into_v8(self, vals):
		dbg("V12TO")
		try:
			dbg("V12TO tryer")
			if v8_mode == 'live':
				v8_password = self.env['ir.config_parameter'].sudo().search([('key','=','v8_password')]).value
				v8 = Client("https://portal.hwseta.org.za/xmlrpc", "HWSETA", "admin", v8_password)
			elif v8_mode == 'test':
				v8_password = self.env['ir.config_parameter'].sudo().search([('key','=','v8_password')]).value
				v8 = Client("http://192.168.15.108:8016/xmlrpc", "mohavia_live_2023_03_01", "admin", "1")
			else:
				raise UserError("System is inconsistent")
			dbg("V12TOV8:", v8)
			v8_res_partner = v8.env['res.partner']
			# check for matching SDLs in 8
			v8_match = v8_res_partner.search([('employer_sdl_no','=',vals['employer_sdl_no'])])
			dbg("V12TOV8:", len(v8_match))
			if len(v8_match) == 0:
				# create a new org in 8
				self.v8_create(v8, vals)
			else:
				# update the org in 8
				self.v8_update(v8, vals)

		except Exception as e:
			raise UserError("Test approve:"+str(e))
			pass

	@api.multi
	def test_import_into_v8(self, vals):
		try:
			if v8_mode == 'live':
				v8_password = self.env['ir.config_parameter'].sudo().search([('key','=','v8_password')]).value
				v8 = Client("https://portal.hwseta.org.za/xmlrpc", "HWSETA", "admin", v8_password)
			elif v8_mode == 'test':
				v8_password = self.env['ir.config_parameter'].sudo().search([('key','=','v8_password')]).value
				v8 = Client("http://192.168.15.108:8016/xmlrpc", "mohavia_live_2023_03_01", "admin", "1")
			else:
				raise UserError("System is inconsistent")
			dbg("V12TOV8:", v8)
		except Exception as e:
			raise UserError("Could not connect to V8 System")
		v8_res_partner = v8.env['res.partner']
		# check for matching SDLs in 8
		v8_match = v8_res_partner.search([('employer_sdl_no','=',vals['employer_sdl_no'])])
		v8_match = v8_res_partner.search([('employer_sdl_no','=','T000000057')])
		dbg("V12TOV8:", len(v8_match))
		if len(v8_match) == 0:
			# create a new org in 8
			self.v8_create(v8, vals)
			dbg(v8, vals)
		else:
			# update the org in 8
			self.v8_update(v8, vals)

	@api.multi
	def modify_rec_data(self, rec_data):
		rec_data_modified={}
		rec_data_modified["child_employer_ids"] = rec_data['child_employer_ids']
		rec_data_modified["name"] = rec_data["name"],
		rec_data_modified["employer_trading_name"] = rec_data["employer_trading_name"],
		rec_data_modified["employer_approval_status_start_date"] = rec_data["employer_approval_start_date"],
		rec_data_modified["employer_approval_status_end_date"] = rec_data["employer_approval_end_date"],
		rec_data_modified["employer_approval_status_num"] = rec_data["employer_approval_status_num"],
		rec_data_modified["employer_site_no"] = rec_data["employer_approval_status_num"],
		rec_data_modified["employer_sdl_no"] = rec_data["employer_sdl_no"],
		rec_data_modified["employer_main_sdl_no"] = rec_data["main_sdl_no"],#"main_sdl_no"] = "L520756919",
		rec_data_modified["empl_sic_code_id"] = rec_data["empl_sic_code_id"], #"sic_code"] = 1,
		rec_data_modified["email"] = rec_data["email"],
		rec_data_modified["ext_bus_cell_number"] = rec_data["ext_bus_cell_number"],#"employer_contact_cell_number"] = "0116076902",
		rec_data_modified["phone"] = rec_data["phone"],
		rec_data_modified["fax"] = rec_data["employer_fax_number"],
		rec_data_modified["phone"] = rec_data["phone"],
		rec_data_modified["website"] = rec_data["website"],
		rec_data_modified["emp_physical_address_1"] = rec_data["employer_physical_address_1"],
		rec_data_modified["emp_physical_address_2"] = rec_data["employer_physical_address_2"],
		rec_data_modified["emp_physical_address_3"] = rec_data["employer_physical_address_3"],
		rec_data_modified["emp_zip_physical"] = rec_data["zip_physical"],
		rec_data_modified["is_company"] = True,
		rec_data_modified["is_active_provider"] = rec_data["is_active_provider"],
		rec_data_modified["active"] = rec_data["active"],
		rec_data_modified["emp_postal_address_1"] = rec_data["postal_address_1"],
		rec_data_modified["emp_postal_address_2"] = rec_data["postal_address_2"],
		rec_data_modified["emp_postal_address_3"] = rec_data["postal_address_3"],
		# rec_data_modified["employer_latitude_degree"] = rec_data["employer_latitude_degree"],
		# rec_data_modified["employer_latitude_minutes"] = rec_data["employer_latitude_minutes"],
		# rec_data_modified["employer_latitude_seconds"] = rec_data["employer_latitude_seconds"]
		# rec_data_modified["employer_longitude_degree"] = rec_data["employer_longitude_degree"]
		# rec_data_modified["employer_longitude_minutes"] = rec_data["employer_longitude_minutes"]
		# rec_data_modified["employer_longitude_seconds"] = rec_data["employer_longitude_seconds"]
		rec_data_modified["emp_reg_number_type"] = rec_data["emp_reg_number_type"]
		rec_data_modified["employer_registration_number"] = rec_data["employer_registration_number"]
		rec_data_modified["vat"] = rec_data["vat"]
		rec_data_modified["emp_levy_paying"] = rec_data["emp_levy_paying"]
		rec_data_modified["emp_non_levy_paying"] = rec_data["emp_non_levy_paying"]
		rec_data_modified["emp_exempt"] = rec_data["emp_exempt"]
		rec_data_modified["emp_government"] = rec_data["emp_government"]
		rec_data_modified["emp_university"] = rec_data["emp_university"]
		rec_data_modified["emp_tvet_college"] = rec_data["emp_tvet_college"]
		rec_data_modified["emp_other_group"] = rec_data["emp_other_group"]
		rec_data_modified["emp_health"] = rec_data["emp_health"]
		rec_data_modified["emp_walfare"] = rec_data["emp_walfare"]
		rec_data_modified["emp_other"] = rec_data["emp_other"]
		rec_data_modified["lang"] = rec_data["lang"]
		rec_data_modified["employees_count"] = rec_data["employees_count"]
		rec_data_modified["total_annual_payroll"] = rec_data["total_annual_payroll"]
		# rm = {}
		# field_list = self.fields_get()
		# for rec in rec_data.keys():
		# 	f_type = field_list[rec]
		# 	if f_type in ['many2many', 'one2many']:
		# 		pass
		# 	elif rec_data_modified[rec]==False or rec_data_modified[rec]==[False]:
		# 		continue
		# 	else:
		# 		pass
		# 	rm[rec] = rec_data_modified[rec]
		# return rm
		return rec_data_modified

	@api.multi
	def test_action_approve(self, vals):
		self.test_import_into_v8(vals)

	@api.multi
	def action_re_approve(self, vals):
		dbg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> hit re-approve")
		dbg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> hit re-approve")
		dbg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> hit re-approve")
		dbg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> hit re-approve")
		# find the res.partner guy
		rp_record = self.env['res.partner'].search([('employer_sdl_no','=',self.employer_sdl_no)])
		if rp_record:
			# raise UserError(rp_record)
			rp_record.unlink()
		dbg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> change to sdp_submitted")
		dbg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> change to sdp_submitted")
		dbg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> change to sdp_submitted")
		dbg(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> change to sdp_submitted")
		self.state = 'sdp_submitted'
		self.sdp_submit = True
		self.sdp_approved = False
		self.approved = False
		self.rejected = False
		self.action_approve(vals)

	@api.multi
	def action_approve(self, vals):
		dbg("action_approve_git")#context = self._context
		context = self._context
		if context is None:
			context = {}
		# self = self.with_context(approved=True)

		###
		if self.record_updated_flg:
			dbg("action_approve_git if self.record_updated_flg:")
			self.state = 'sdp_approved'
			self.sdp_approved = True

			all_data = self.read()
			all_data = self.tuple_fixer(all_data)

			rec_data = {}
			for key in all_data[0]:
				# if key == 'ref':
				#	continue
				if key == 'message_ids':
					# o2m mail.message
					continue
				if key == 'message_follower_ids':
					# o2m mail.followers
					continue
				if key == 'activity_ids':
					# o2m contacts
					continue

				rec_data[key] = all_data[0][key]
			# field = self._fields[key]

			# self.env['res.partner'].write(rec_data)

			# Cast to write bank accounts from O2m wizard
			dbg('rec_data0: ' + str(rec_data))
			update_res = self.env['res.partner'].search([('employer_sdl_no', '=', rec_data['employer_sdl_no'])])
			dbg('action_approve_git rec_data0:'+str(update_res))
			org_bnks = []
			bnk_dict = {}
			bank_account_partner = []
			bank_account_numbers = []
			if update_res:
				dbg("action_approve_git if _update_res:")
				for i in rec_data['bank_ids']:
					org_bnks.append(i)

				dbg('org banks appr ' + str(org_bnks))
				del rec_data['bank_ids']
				for acc in org_bnks:
					bnk = self.env['organization.bank.account'].search([('id', '=', acc)])
					dbg(self.env.cr.execute('SELECT * FROM organization_bank_account where id = %s', [acc]))
					dbg(self.env.cr.fetchall())
					dbg('org banks ids ' + str(bnk['bank_id']))
					bnk_dict.update({'acc_number': bnk['acc_number'],
									 'sanitized_acc_number': bnk['sanitized_acc_number'],
									 'acc_holder_name': bnk['acc_holder_name'],
									 'bank_id': bnk['bank_id'].id,
									 'sequence': bnk['sequence'],
									 'currency_id': bnk['currency_id'].id,
									 'company_id': bnk['company_id'].id,
									 'active': bnk['active'],
									 'mandatory': bnk['mandatory'],
									 'state': bnk['state'],
									 'discretionary': bnk['discretionary'],
									 'action_date': bnk['action_date'],
									 'usage_date': bnk['usage_date'],
									 'partner_id': bnk['partner_id'].id,
									 'create_uid': bnk['create_uid'].id,
									 'write_uid': bnk['write_uid'].id,
									 'create_date': bnk['create_date'],
									 'write_date': bnk['write_date']
									 })
					dbg(bnk_dict)

					id_ = self.env['res.partner.bank'].create(bnk_dict)

					bank_account_partner.append(id_)
					bank_account_numbers.append(bnk['acc_number'])
					dbg('sasha: ' + str(bank_account_numbers))

			dict_cpy = {}
			dict_cpy = rec_data.copy()

			del rec_data['mandatory_account']
			del rec_data['discretionary_account']

			del dict_cpy['mandatory_account']
			del dict_cpy['discretionary_account']

			for key in dict_cpy:
				if dict_cpy[key]:
					dbg(str(key) + ' ===== ' + str(rec_data[key]))

				update_res.write({key: dict_cpy[key]})
			update_res.write(rec_data)

			update_res.update({'bank_ids': [(6, 0, [x.id for x in self.bank_ids])]})
			self.record_updated_flg = False
			# dbg("action_approve_git obj_res"+str(obj_res))
			
			rec_data_modified = self.modify_rec_data(rec_data)
			imported_v8 = self.import_into_v8(rec_data_modified)
			dbg("action_approve_git V12TOV8", imported_v8)
			# active bank acc updates
			active_man_acc = self.mandatory_account.read()
			active_disc_acc = self.discretionary_account.read()
			if active_disc_acc:
				if active_disc_acc[0]['discretionary']:
					disc_acc = self.env['res.partner.bank'].search([('acc_number', '=', active_disc_acc[0]['acc_number'])])
					dbg('disc_acc: ' + str(disc_acc))
					update_res.write({'discretionary_account': disc_acc.id})
			if active_man_acc:
				if active_man_acc[0]['mandatory']:
					mand_acc = self.env['res.partner.bank'].search([('acc_number', '=', active_man_acc[0]['acc_number'])])
					dbg('mand_acc: ' + str(mand_acc))
					update_res.write({'mandatory_account': mand_acc.id})


			dbg('self bank ids:' + str(self.bank_ids))
			dbg(bank_account_partner)
			for acc in bank_account_partner:
				dbg(acc)
				update_res.write({'bank_ids': acc})


			# update_res.update({'bank_ids': [(6, 0, [x.id for x in bank_account_partner])]})
			# self.record_updated_flg = False

		if self.sdp_submit == True and self.state == 'sdp_submitted' and self.approved == False:
			dbg("action_approve_git self.sdp_submit == True and self.state == 'sdp_submitted' and self.approved == False:")
			self.state = 'sdp_approved'
			self.sdp_approved = True

			if self.imported_updated_flg:
				pass
			else:
				t_num = self.env['ir.sequence'].get('organization_t_number')
				aa = dict(self._fields['alt_sdl_prefix'].selection).get(self.alt_sdl_prefix)
				org_t_number = aa + str(t_num)
				self.employer_sdl_no = org_t_number

			all_data = self.read()
			all_data = self.tuple_fixer(all_data)

			rec_data = {}
			for key in all_data[0]:
				# if key == 'ref':
				#	continue
				if key == 'message_ids':
					# o2m mail.message
					continue
				if key == 'message_follower_ids':
					# o2m mail.followers
					continue
				if key == 'activity_ids':
					# o2m contacts
					continue

				rec_data[key] = all_data[0][key]
				# dbg(key + " <> " + str(all_data[0][key]))

				field = self._fields[key]

			# self.env['res.partner'].write(rec_data)

			# Cast to write bank accounts from O2m wizard
			# dbg('action_approve_git rec_data_: ' + str(rec_data))
			####Handle for internal ref issue: del rec_data['ref']
			update_res = self.env['res.partner'].sudo().search([('employer_sdl_no', '=', rec_data['employer_sdl_no'])])
			dbg("action_approve_git" + str(rec_data['employer_sdl_no']))
			dbg("action_approve_git" + str(update_res))
			org_bnks = []
			bnk_dict = {}
			if update_res:
				dbg("action_approve_git if update_res:")
				for i in rec_data['bank_ids']:
					org_bnks.append(i)

				del rec_data['bank_ids']
				for acc in org_bnks:
					bnk = self.env['organization.bank.account'].search([('id', '=', acc)])
					dbg(self.env.cr.execute('SELECT * FROM organization_bank_account where id = %s', [acc]))
					dbg(self.env.cr.fetchall())
					bnk_dict.update({'acc_number': bnk['acc_number'],
									 'sanitized_acc_number': bnk['sanitized_acc_number'],
									 'acc_holder_name': bnk['acc_holder_name'],
									 'bank_id': bnk['bank_id'].id,
									 'sequence': bnk['sequence'],
									 'currency_id': bnk['currency_id'].id,
									 'company_id': bnk['company_id'].id,
									 'active': bnk['active'],
									 'mandatory': bnk['mandatory'],
									 'state': bnk['state'],
									 'discretionary': bnk['discretionary'],
									 'action_date': bnk['action_date'],
									 'usage_date': bnk['usage_date'],
									 'partner_id': bnk['partner_id'].id,
									 'create_uid': bnk['create_uid'].id,
									 'write_uid': bnk['write_uid'].id,
									 'create_date': bnk['create_date'],
									 'write_date': bnk['write_date']
									 })
					dbg(bnk_dict)

					self.env['res.partner.bank'].create(bnk_dict)

				# handle for internal ref
				# del rec_data['ref']
				update_res.write(rec_data)
				update_res.update({'bank_ids': [(6, 0, [x.id for x in self.bank_ids])]})


			else:
				dbg("del rec_data['statssa_area_code']")

			# handle for internal ref
			del rec_data['ref']
			obj_res = self.env['res.partner'].create(rec_data)
			dbg("action_approve_git obj_res"+str(obj_res))
			rec_data_modified = self.modify_rec_data(rec_data)
			imported_v8 = self.import_into_v8(rec_data_modified)
			dbg("action_approve_git V12TOV8", imported_v8)
			dbg(rec_data)
			return super(organizationMeta, self).write(rec_data)
		elif self.state == 'submitted' and self.employer_sdl_no:
			dbg("action_approve_git" + str("elif self.state == 'submitted' and self.employer_sdl_no"))
			# Change to carter for updating currnent res records
			self.state = 'sdp_approved'
			self.sdp_approved = True

			all_data = self.read()
			all_data = self.tuple_fixer(all_data)

			rec_data = {}
			for key in all_data[0]:
				# if key == 'ref':
				#	continue
				if key == 'message_ids':
					# o2m mail.message
					continue
				if key == 'message_follower_ids':
					# o2m mail.followers
					continue
				if key == 'activity_ids':
					# o2m contacts
					continue

				rec_data[key] = all_data[0][key]
				# dbg(key + " <> " + str(all_data[0][key]))

				field = self._fields[key]
			# dbg('action_approve_git rec data' + str(rec_data))

			# #manual override int subscrptable
			# org_record = self.env['organization.meta'].search([('id', '=', rec_data['id'])])
			# del rec_data['id']
			# org_record.write(rec_data)

			# super(organizationMeta, self).write(rec_data)
			res_id = self.env['res.partner'].search([('employer_sdl_no', '=', self.employer_sdl_no)])
			# updated bank accounts migration from org banks
			# rec_data.update({'bank_ids': [(6, 0, [x.id for x in self.bank_ids])]})
			dbg(self.bank_ids)
			dbg(res_id['bank_ids'])
			dbg([x for x in self.bank_ids])
			rec_data.update({'bank_ids': [(6, 0, [x.id for x in self.bank_ids])]})
			del rec_data['fin_submit']
			del rec_data['prefix_g']
			del rec_data['partner_id']
			del rec_data['site_no']
			# del rec_data['partner_gid']
			del rec_data['vendor']
			del rec_data['submitted']
			del rec_data['approved']
			del rec_data['rejected']
			del rec_data['record_updated_flg']
			del rec_data['imported_updated_flg']
			del rec_data['sdp_submit']
			del rec_data['sdp_approved']
			del rec_data['id']
			del rec_data['page']
			# dbg("action_approve_git"+str(rec_data))

			dbg(rec_data)
			res_id.update(rec_data)

			dbg('action_approve_git Inside Fin approve cycle')
			activity_obj = self.env['mail.activity']
			vals = {}
			vals['res_model'] = 'organization.meta'
			vals['res_id'] = self.id
			vals['res_model_id'] = self.env['ir.model'].search([('model', '=', 'organization.meta'), ]).id
			vals['email_from'] = self.env['res.partner'].search([('id', '=', self.env.uid), ]).email

			activity_obj.create(vals)
			rec_data_modified = self.modify_rec_data(rec_data)
			imported_v8 = self.import_into_v8(rec_data_modified)
			dbg("action_approve_git V12TOV8", imported_v8)
			# raise UserError("stopping for test purposes")
			return self.filtered(lambda proj: proj.state in ('submitted', 'sdp_approved', 'fin_submitted')).write({
				'state': 'approved',
				'approved': True
			})

	def tuple_fixer(self, vals):
		for val in vals[0].keys():
			# dbg(vals[0].get(val))
			# dbg(type(vals[0].get(val)))
			if type(vals[0].get(val)) == tuple:
				vals[0].update({val: vals[0].get(val)[0]})
		return vals

	@api.multi
	def action_rollback_state(self):
		# TODO: rollback state stuff
		if self.state == 'sdp_submitted':
			return self.filtered(
				lambda org: org.state in ('submitted', 'rejected', 'sdp_approved', 'sdp_submitted')).write({
				'state': 'draft',
				'submitted': False,
				'sdp_submit': False,
				'sdp_approved': False,
				'rejected': False,
			})
		if self.state == 'submitted':
			return self.filtered(
				lambda org: org.state in ('submitted', 'rejected', 'sdp_approved', 'sdp_submitted')).write({
				'state': 'sdp_submitted',
				'submitted': False,
				'sdp_submit': False,
				'sdp_approved': False,
				'rejected': False,
			})
		if self.state == 'rejected':
			return self.filtered(
				lambda org: org.state in ('submitted', 'rejected', 'sdp_approved', 'sdp_submitted')).write({
				'state': 'draft',
				'submitted': False,
				'sdp_submit': False,
				'sdp_approved': False,
				'rejected': False,
			})

	@api.multi
	def action_reject(self):
		activity_obj = self.env['mail.activity']
		vals = {}
		vals['res_model'] = 'organization.meta'
		vals['res_id'] = self.id
		vals['res_model_id'] = self.env['ir.model'].search([('model', '=', 'organization.meta'), ]).id
		vals['email_from'] = self.env['res.partner'].search([('id', '=', self.env.uid), ]).email

		activity_obj.create(vals)
		return self.filtered(
			lambda project: project.state in ('submitted', 'rejected', 'sdp_approved', 'sdp_submitted')).write(
			{'state': 'rejected',
			 'rejected': True})

	@api.multi
	def action_submit(self):
		# cast to limit sequence progression to only T numbers.
		# Update seperate seq for others
		if self.alt_sdl_prefix == 'prefix_T':
			# cast to limit sequence progression to only T numbers. Update seperate seq for others
			self.ensure_one()
			all_fields = self.read()
			dbg(all_fields)

			activity_obj = self.env['mail.activity']
			vals = {}
			vals['res_model'] = 'organization.meta'
			vals['res_id'] = self.id
			vals['res_model_id'] = self.env['ir.model'].search([('model', '=', 'organization.meta'), ]).id
			vals['email_from'] = self.env['res.partner'].search([('id', '=', self.env.uid), ]).email

			activity_obj.create(vals)

			return self.filtered(lambda org: org.state in ('draft')).write(
				{'state': 'sdp_submitted', 'sdp_submit': True})
		else:
			if not self.imported_updated_flg:
				raise UserError(
					'Only T Number generation is currently enabled. Please Use T prefixes or log a tickect with helpdesk support')
			else:
				return self.filtered(lambda org: org.state in ('draft')).write(
					{'state': 'sdp_submitted', 'sdp_submit': True})

	@api.multi
	def action_request_approval(self):
		approver_group = self.env.ref("hwseta_finance.group_approve_journal_entries")
		ctx = {
			"default_res_model_id": self.env.ref("hwseta_project.organization.meta").id,
			"default_res_id": self.ids[0],
			"default_res_name": self.name,
			"default_activity_type_id": self.env.ref(
				"hwseta_finance.mail_activity_approve_journal_entry"
			).id,
			"default_group_id": approver_group.id,
			"group_id": approver_group.id,
			# 'default_view_id': self.env.ref('hwseta_finance.organisation_voucher_form').id
		}
		action = self.env.ref(
			"hwseta_finance.action_view_mail_activity_form_popup"
		).read()[0]
		action.update({"target": "new"})

		action.update({"context": ctx})

		self.write({"state": "to_approve"})
		return action


class OrganizationBankAccounts(models.Model):
	_name = 'organization.bank.account'
	# _inherit = 'res.partner.bank'
	# _inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'acc_number'
	_description = 'Organization Banking details staginzg table'
	_sql_constraints = [('unique_number', 'check(1=1)', 'Bank account exists'), ]

	def sanitize_account_number(acc_number):
		if acc_number:
			return re.sub(r'\W+', '', acc_number).upper()
		return False

	@api.model
	def retrieve_acc_type(self, acc_number):
		""" To be overridden by subclasses in order to support other account_types.
		"""
		return 'bank'

	acc_type = fields.Selection(selection=lambda x: x.env['res.partner.bank'].get_supported_account_types(),
								compute='_compute_acc_type', string='Type',
								help='Bank account type: Normal or IBAN. Inferred from the bank account number.')
	acc_number = fields.Char('Account Number', required=True)
	sanitized_acc_number = fields.Char(compute='_compute_sanitized_acc_number', string='Sanitized Account Number',
									   readonly=True, store=True)
	acc_holder_name = fields.Char(string='Account Holder Name',
								  help="Account holder name, in case it is different than the name of the Account Holder")
	partner_id = fields.Many2one('res.partner', 'Account Holder', ondelete='cascade', index=True,
								 domain=['|', ('is_company', '=', True), ('parent_id', '=', False)], required=False)
	org_meta_id = fields.Many2one('organization.meta', 'Account Holder', ondelete='cascade', index=True,
								  domain=['|', ('is_company', '=', True), ('parent_id', '=', False)], required=False)
	bank_id = fields.Many2one('res.bank', string='Bank')
	bank_name = fields.Char(related='bank_id.name', readonly=False)
	bank_bic = fields.Char(related='bank_id.bic', readonly=False)
	sequence = fields.Integer(default=10)
	currency_id = fields.Many2one('res.currency', string='Currency')
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id,
								 ondelete='cascade')
	qr_code_valid = fields.Boolean(string="Has all required arguments", compute="_validate_qr_code_arguments")

	mandatory = fields.Boolean(track_visibility='always')
	discretionary = fields.Boolean(track_visibility='always')
	active = fields.Boolean(default=True)
	is_active = fields.Boolean(string="Active acc", default=True)
	# state = fields.Selection([('draft','Draft'),('submitted', 'Submitted'),('approved','Approved'),('rejected', 'Rejected')],default='draft', track_visibility='always')
	state = fields.Selection([('created', 'Created'), ('approved', 'Approved'), ('rejected', 'Rejected')],
							 default='created', track_visibility='always')
	action_date = fields.Date(track_visibility='always')
	usage_date = fields.Date(track_visibility='always')

	@api.depends('acc_number')
	def _compute_sanitized_acc_number(self):
		for bank in self:
			bank.sanitized_acc_number = self.sanitize_account_number(bank.acc_number)

	@api.depends('acc_number')
	def _compute_acc_type(self):
		for bank in self:
			bank.acc_type = self.retrieve_acc_type(bank.acc_number)

	@api.multi
	def _validate_qr_code_arguments(self):
		for bank in self:
			bank.qr_code_valid = (bank.bank_bic
								  and bank.company_id.name
								  and bank.acc_number)

	def bank_account_duplicate_check(self, bank_account_number):
		bank_account_checker = self.env['organization.bank.account'].search([])
		for bank_exists in bank_account_checker:
			if bank_exists.acc_number == bank_account_number:
				return False
			else:
				return True

	@api.multi
	def reject_bank_account(self):
		self.state = 'rejected'
		self.active = 'false'
		self.action_date = dt.date.today()
		self.partner_id.chatter(self.env.user,
								'user has rejected this bank:' + self.acc_number)

	@api.multi
	def approve_bank_account(self):
		not_same_uid = False
		right_state = False
		invoke = False
		accs = self.env['organization.bank.account'].search(
			[('acc_number', '=', self.acc_number), ('id', '!=', self.id), ('state', '=', 'approved')])
		if accs:
			dbg(accs)
			invoke = True
		if self.create_uid.id != self.env.user.id or self.env.user.id == 2:
			not_same_uid = True
		if self.state == 'created':
			right_state = True
		if self.state != 'created':
			raise Warning(_("You cannot approve a bank account that is not submitted."))
		elif right_state and not_same_uid and not invoke:
			self.state = 'approved'
			self.action_date = dt.date.today()
			self.partner_id.chatter(self.env.user,
									'user has approved this bank:' + self.acc_number)
		elif right_state and not_same_uid and invoke:

			msg = ''
			for dupe in accs:
				if dupe.partner_id.employer_sdl_no:
					ident = dupe.partner_id.employer_sdl_no
				else:
					ident = dupe.partner_id.ref
				msg += 'account holder:' + dupe.partner_id.name + '>' + ident + ' -account number:' + dupe.acc_number + ' -bank name:' + dupe.bank_id.name + '\n'
			wizard_id = self.env['bank.account.wizard'].create({
				'is_approved': False,
				'msg': msg,
			})
			ret = {
				'type': 'ir.actions.act_window',
				'name': _('Random Sample'),
				'res_model': 'bank.account.wizard',
				'res_id': wizard_id.id,
				'view_mode': 'form',
				'view_type': 'form',
				'target': 'new',
			}
			dbg(ret)
			return ret

		else:
			if self.create_uid == self.env.user.id:
				raise Warning(_("You cannot approve a bank record that you created"))

	@api.model
	def create(self, vals):
		# if self.partner_id.employer:
		#	  template_obj = self.env.ref('banking_detail_change_email_template').read()[0]
		#	  template_obj.send_mail()
		bank_account = super(OrganizationBankAccounts, self).create(vals)
		bank_account.partner_id.chatter(self.env.user,
										'user has created this bank:' + bank_account.acc_number)
		if bank_account and bank_account.partner_id.is_employer:
			bank_details_changes_group = self.env.ref('hwseta_finance.group_bank_account_changes_notifications')
			for user in bank_details_changes_group.users:
				notification_values = {'user_id': user.id}
		# activities = bank_account.activity_schedule('hwseta_finance.mail_activity_banking_details_changed',
		# 											None, 'Changes to bank account details - Summary',
		# 											'Changes to bank account details - Note',
		# 											**notification_values)

		return bank_account

	def write(self, vals):
		# if self.partner_id.employer:
		#	  template_obj = self.env.ref('banking_detail_change_email_template').read()[0]
		#	  template_obj.send_mail()
		# raise UserError("{}".format(vals))
		bank_account = super(OrganizationBankAccounts, self).write(vals)

		if bank_account and self.partner_id.is_employer:
			bank_details_changes_group = self.env.ref('hwseta_finance.group_bank_account_changes_notifications')
			for user in bank_details_changes_group.users:
				notification_values = {'user_id': user.id}
		# activities = self.activity_schedule('hwseta_finance.mail_activity_banking_details_changed', None,
		# 									'Changes to bank account details - Summary',
		# 									'Changes to bank account details - Note', **notification_values)
		return bank_account

	@api.multi
	def unlink(self):
		for ba in self:
			msg = 'deleted the bank account:' + str(ba.acc_number) + ' mandatory:' + str(
				ba.mandatory) + ' discretionary:' + str(ba.discretionary)
			ba.partner_id.chatter(self.env.user, msg)
		return super(OrganizationBankAccounts, self).unlink()

class organizationMetaV8Log(models.Model):
	_name = 'organization.meta.v8.log'
	_description = "Log updates or creates on V8"

	name = fields.Char()
	create_or_update = fields.Selection([
		('create', 'Create'),
		('update', 'Update'),
	], default='create')
	approver_on_12 = fields.Char()
	status = fields.Selection([
		('success', 'Success'),
		('error', 'Error'),
	])
	message = fields.Char()


# Clever trick to circumnavigate partner can't follow twice'
class Followers(models.Model):
	_inherit = 'mail.followers'

	@api.model
	def create(self, vals):
		if 'res_model' in vals and 'res_id' in vals and 'partner_id' in vals:
			dups = self.env['mail.followers'].search([('res_model', '=', vals.get('res_model')),
													  ('res_id', '=', vals.get('res_id')),
													  ('partner_id', '=', vals.get('partner_id'))])
			if len(dups):
				for p in dups:
					p.unlink()
		return super(Followers, self).create(vals)