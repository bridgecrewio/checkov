from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.gcp.AbsGooglePostgresqlDatabaseFlags import AbsGooglePostgresqlDatabaseFlags

FLAG_NAME = 'log_min_error_statement'
FLAG_VALUES = [
    "debug5",
    "debug4",
    "debug3",
    "debug2",
    "debug1",
    "info",
    "notice",
    "warning",
    "error"
]


class GoogleCloudPostgreSqlLogMinErrorStatement(AbsGooglePostgresqlDatabaseFlags):
    def __init__(self):
        name = "Ensure the GCP PostgreSQL database log levels are set to ERROR or lower"
        check_id = "CKV_GCP_109"
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


check = GoogleCloudPostgreSqlLogMinErrorStatement()
