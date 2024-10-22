# no False Positive - where it's not an actual secret
check_metadata_values = ('bafadssda$#%2', 'bdfsver#$@%')
CHECKOV_METADATA_RESULT = 'checkov_results5243gvr'
check1 = {'blabla': 'blabla1'}
check2 = {'blabla': 'blabla2'}
check1['some_key_1235#$@'] = check2.get('some_value_1235')


access_key = "AKIAIOSFODNN7EXAMPLE"
secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
if __name__ == '__main__':
    print('secrets')