#%%
import sys
print(sys.version)
print(sys.executable)
print(sys.path)
print("Initialization complete.")

#%%
import os

# os.environ['PATH'] = 'C:\SAPNWRFC_750\lib;' + os.environ['PATH']
# os.environ["SAPNWRFC_HOME"] = 'C:\SAPNWRFC_750'

import pprint

import pyrfc

#%%
conn = pyrfc.Connection(
    
    user=os.getenv("SAP_USER", ""),
    passwd=os.getenv("SAP_PASSWORD", ""),
    ashost=os.getenv("SAP_ASHOST", ""),
    sysnr=os.getenv("SAP_SYSNR", ""),
    client=os.getenv("SAP_CLIENT", ""),
    lang=os.getenv("SAP_LANG", ""),
    trace=os.getenv("SAP_TRACE", ""),

    # saprouter='string',
    # sysid='string',
    # group='string',
    # mshost='string',
    # r3name='string',
    # group_name='string',
    # codepage='string',
    # no_snc='string',
    # snc_qop='string',
    # snc_myname='string',
    # snc_lib='string',
    # x509cert='string',
    # dest='string',
    # timeout='string',
    # trace='string'
)
result = conn.call('RFC_SYSTEM_INFO')
pprint.pprint(result)


#%%
def get_rfc_functions(conn, funcs_mask=None, devclass=None):
    fields = ['FUNCNAME', 'DEVCLASS', 'STEXT']
    options = []

    if '*' in funcs_mask:
        funcs_mask = funcs_mask.replace('*', '%')
        options.append({'TEXT': f"FUNCNAME LIKE '{funcs_mask}'"})
    elif funcs_mask:
        #funcs_mask = f'"{funcs_mask}%"'
        options.append({'TEXT': f"FUNCNAME = '{funcs_mask}'"})

    if devclass:
        if '*' in devclass:
            devclass = devclass.replace('*', '%')
            devclass_mask = f"'{devclass}%'"
            options.append({'TEXT': f"AND DEVCLASS LIKE '{devclass_mask}'"})
        else:
            options.append({'TEXT': f"AND DEVCLASS = ''{devclass}'"})

    options.append({'TEXT': "AND FMODE = 'R'"})

    print(f"{funcs_mask=}, {devclass=}, {fields=}, {options=}")

    result = conn.call('RFC_READ_TABLE', 
                        QUERY_TABLE='INFO_FUNCT', 
                        DELIMITER='|',
                        FIELDS=fields, OPTIONS=options)
    print(result)

    data = []
    if 'DATA' in result:
        for row in result['DATA']:
            row = {field: value.strip() for field, value in zip(fields, row['WA'].split('|'))}
            # if funcs_mask and not row['FUNCNAME'].startswith(funcs_mask):
            #     continue
            data.append(row)
    return data

#%%
get_rfc_functions(conn, funcs_mask='RFC_*')
#%%
get_rfc_functions(conn, funcs_mask='RFC_PING', devclass='SAPBC')
#%%



params = conn.get_function_description('Z_SEND_EXTERNAL_MAIL')
print(f"Function Parameters: {params.name}" )
for param in params.parameters:
    print(param)
# %%
