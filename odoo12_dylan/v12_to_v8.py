import xmlrpc.client
from urllib.parse import urljoin, urlparse

# odoo_url12 = 'https://projects.hwseta.org.za'
odoo_url12 = 'http://localhost:8012'
sdl_list = ['T110002711', 'T110002720']
pref_sdl_list = ['L530821372','L710821374']
[
                                            'name',
                                            'ref',
                                            'employer_sdl_no',
                                            'employer_trading_name',
                                            'lang',
                                            'phone'
                                            'mobile'
                                            'street'
                                            'street2'
                                            'street3'
                                            'sars_number'
                                            'ext_date_of_birth'
                                            'ext_date_business_commenced'
                                            'ext_date_person_became_liable'
                                            'ext_identity_number'
                                            'ext_empl_sic_code_id'
                                            'ext_postal_address_1'
                                            'ext_postal_address_2'
                                            'ext_postal_address_3'
                                            'ext_postal_code'
                                            ]
field_map = {
    'name':'name',
    'employer_trading_name':'employer_trading_name',
    # 'employer_approval_start_date':'',
    # 'employer_approval_end_date':'',
    'emp_levy_paying':'emp_levy_paying',
    'emp_non_levy_paying':'emp_non_levy_paying',
    'emp_exempt':'emp_exempt',
    'emp_government':'emp_government',
    'emp_university':'emp_university',
    'emp_tvet_college':'emp_tvet_college',
    'emp_other_group':'emp_other_group',
    'emp_health':'emp_health',
    'emp_walfare':'emp_welfare',
    'emp_other':'emp_other',
    'emp_reg_number_type':'emp_reg_number_type',
    'employer_sdl_no':'employer_sdl_no',
    'employer_site_no':'employer_site_no',
    'employer_registration_number':'employer_registration_number',
    'vat':'employer_vat_number',
    'website':'website',
    'seta_id':'employer_seta_id',
    'sic_code':'empl_sic_code_id',
    # 'employer_contact_name':'',
    # 'employer_contact_phone_number':'',
    'employer_phone_number':'phone',
    'employer_contact_cell_number':'mobile',
    'employer_fax_number':'fax',
    'employer_contact_email_address':'email',
    'employer_physical_address_1':'emp_physical_address_1',
    'employer_physical_address_2':'emp_physical_address_2',
    'employer_physical_address_3':'emp_physical_address_3',
    'employer_physical_address_code':'emp_zip_physical',
    'employer_postal_address_1':'emp_postal_address_1',
    'employer_postal_address_2':'emp_postal_address_2',
    'employer_postal_address_3':'emp_postal_address_3',
    'employer_postal_address_code':'emp_zip_postal',
    # manually found, not part of map provided
    'sars_number':'sars_number',
    'ext_date_of_birth':'ext_date_of_birth',
    'ext_date_business_commenced':'ext_date_business_commenced',
    'ext_date_person_became_liable':'ext_date_person_became_liable',
    'ext_identity_number':'ext_identity_number',
    'ext_empl_sic_code_id':'ext_empl_sic_code_id',
    'ext_postal_address_1':'ext_postal_address_1',
    'ext_postal_address_2':'ext_postal_address_2',
    'ext_postal_address_3':'ext_postal_address_3',
    'ext_postal_code':'ext_postal_code',
}

# odoo_dbname12 = 'hwseta'
# # odoo_dbname8 = 'live_2022_12_13'
# odoo_user12 = 'admin'
# odoo_pass12 = 'k0u[~l@5Ml43tpr'

odoo_dbname12 = '17_March_2023'
# odoo_dbname8 = 'live_2022_12_13'
odoo_user12 = 'admin'
odoo_pass12 = '1'

odoo_url8 = 'https://portal.hwseta.org.za'
# odoo_url8 = 'https://workshop.hwseta.org.za'
# odoo_dbname8 = 'live_01_24'
odoo_dbname8 = 'HWSETA'
odoo_user8 = 'admin'
odoo_pass8 = 'k0u[~l@5Ml43tpr'
# odoo_pass8 = 'admin'

# odoo_url8 = 'http://192.168.15.108:8053'
# # odoo_dbname8 = 'live_01_24'
# odoo_dbname8 = 'mohavia_live_2023_03_01'
# odoo_user8 = 'admin'
# odoo_pass8 = '1'
# these are user logins(seems they have changed l-num on partner but the original user still has old num as the login)
bad_list=['L050705625','T110000123','L780763803']


def connect(odoo_url=None,odoo_dbname=None,odoo_user=None,odoo_pass=None):
    print(f"odoo_url={odoo_url},odoo_dbname={odoo_dbname},odoo_user={odoo_user},odoo_pass={odoo_pass}")
    common = xmlrpc.client.ServerProxy(urljoin(odoo_url, '/xmlrpc/2/common'))
    print(common)
    try:
        uid = common.authenticate(odoo_dbname, odoo_user, odoo_pass, {})
        print(uid)
    # uid = common.login(odoo_dbname, odoo_user, odoo_pass, {})
    except Exception as e:
        print(e)
        pass
    if uid:
        return uid
    else:
        raise Warning("no uid found")


def run_script():
    uid12 = connect(odoo_url12,odoo_dbname12,odoo_user12,odoo_pass12)
    models = xmlrpc.client.ServerProxy(odoo_url12 + '/xmlrpc/2/object')
    uid8 = connect(odoo_url8, odoo_dbname8, odoo_user8, odoo_pass8)
    models8 = xmlrpc.client.ServerProxy(odoo_url8 + '/xmlrpc/2/object')
    if uid12 and uid8:
        users_match = models8.execute_kw(odoo_dbname8, uid8, odoo_pass8,
                                'res.users',
                                'search', [[['login','in',sdl_list]]])
        print(users_match)
        users_fields_list = models8.execute_kw(odoo_dbname8, uid8, odoo_pass8,
                                        'res.users', 'read',
                                        [users_match],
                                        {'fields':
                                             ['id','partner_id','login']
                                         }
                                        )
        # print(users_fields_list)
        for u in users_fields_list:
            print(u)
        new_orgs = models.execute_kw(odoo_dbname12, uid12, odoo_pass12,
                                'res.partner',
                                'search', [[['employer_sdl_no','in',sdl_list]]])
        # new_orgs = models.execute_kw(odoo_dbname12, uid12, odoo_pass12,
        #                         'res.partner',
        #                         'search', [[['employer_sdl_no','in',pref_sdl_list]]])


        print(len(new_orgs))
        fields_list = models.execute_kw(odoo_dbname12, uid12, odoo_pass12,
                                  'res.partner', 'read',
                                  [new_orgs],
                                        {'fields':
                                            [x for x in field_map.values()]
                                        }
                                        )
        email_list = [x['email'] for x in fields_list]
        # bad_sdl = [x['employer_sdl_no'] for x in fields_list]
        print(email_list)
        users_match = models8.execute_kw(odoo_dbname8, uid8, odoo_pass8,
                                        'res.users',
                                        'search', [[['login', 'in', email_list]]])
        print(users_match)
        users_fields_list = models8.execute_kw(odoo_dbname8, uid8, odoo_pass8,
                                              'res.users', 'read',
                                              [users_match],
                                              {'fields':
                                                   ['id', 'partner_id', 'login']
                                               }
                                              )
        # print(users_fields_list)
        for u in users_fields_list:
            print(u)

        new_emp_list = []
        for emp in fields_list:
            emp_vals = {}
            bad_logins = [x['login'] for x in users_fields_list]
            if emp['employer_sdl_no'] not in [x['employer_sdl_no'] for x in new_emp_list] and emp['email'] not in bad_list and emp['email'] not in bad_logins and emp['employer_sdl_no'] not in pref_sdl_list:
                for k in emp.keys():
                    emp_vals.update({k:emp[k]})
                new_emp_list.append(emp_vals)


        for emp in new_emp_list:
            print(emp)
            emp['employer'] = True
            emp_mod = models8.execute_kw(odoo_dbname8, uid8, odoo_pass8, 'res.partner', 'create', [emp])





if __name__ == "__main__":
    run_script()