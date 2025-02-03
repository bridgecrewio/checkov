from checkov.secrets.runner import should_filter_vault_secret

HIGH_ENTROPY_CHECK_ID = 'CKV_SECRET_80'

def test_vault_secrets_false_positives():

    fp_secrets = [
        'DB_RBMQ_PASSWORD: vault: secret/data/product-web/mcrp-qwr-v2/mabbot#PASSWORD',
        'WEB_PASSWORD: vault: secret/data/product/fwrp-qe-v3/parme3#PASSWORD',
        'PASS: vault: secret/sr/dt/pro/fwrtq1#2/weg#PASSWORD'
    ]
    for fp_secret in fp_secrets:
        assert should_filter_vault_secret(fp_secret, HIGH_ENTROPY_CHECK_ID)

def test_secrets_without_vault():
    real_secrets = [
        'ldap_pwd = k%udk423u4%P8=H_',
        'password = J6T4ww+##14m',
        'PS = 1r4#Gf2FDF$343r3m2me3r%'
    ]
    for real_secret in real_secrets:
        assert not should_filter_vault_secret(real_secret, HIGH_ENTROPY_CHECK_ID)