from __future__ import annotations

def mock_get_empty_license_statuses_async(session, packages, image_name: str):
    return {'image_name': image_name, 'licenses': []}


def mock_get_license_statuses_async(session, packages, image_name: str) -> dict[str, str | list[dict[str, str]]]:
    return {
        "image_name": image_name,
        "licenses": [
            {
                "package_name": "openssl",
                "package_version": "1.1.1q-r0",
                "policy": "BC_LIC_1",
                "license": "OpenSSL",
                "status": "OPEN",
            },
            {
                "package_name": "musl",
                "package_version": "1.2.3-r0",
                "policy": "BC_LIC_1",
                "license": "MIT",
                "status": "COMPLIANT",
            },
        ]
    }
