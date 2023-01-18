def mock_get_empty_license_statuses_async(session, packages, image_name: str):
    return {'image_name': image_name, 'licenses': []}
