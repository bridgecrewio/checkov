from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.gcp.AbsGooglePostgresqlDatabaseFlags import AbsGooglePostgresqlDatabaseFlags

FLAG_NAME = 'cloudsql.enable_pgaudit'
FLAG_VALUES = ['on']


class GoogleCloudPostgreSqlEnablePgaudit(AbsGooglePostgresqlDatabaseFlags):
    def __init__(self):
        name = "Ensure pgAudit is enabled for your GCP PostgreSQL database"
        check_id = "CKV_GCP_110"
        supported_resources = ['google_sql_database_instance']
        categories = [CheckCategories.LOGGING]
        super().__init__(
            name=name,
            id=check_id,
            categories=categories,
            supported_resources=supported_resources,
            flag_name=FLAG_NAME,
            flag_values=FLAG_VALUES
        )


check = GoogleCloudPostgreSqlEnablePgaudit()
