---
layout: default
published: true
title: CycloneDX BOM
nav_order: 20
---

# CycloneDX BOM

CycloneDX is a lightweight BOM specification that is easily created, human-readable, and simple to parse.

A typical output looks like this
```xml
<?xml version="1.0" encoding="UTF-8"?>
<bom xmlns="http://cyclonedx.org/schema/bom/1.4" version="1"
     serialNumber="urn:uuid:b1e6590c-5767-4977-8615-1cd649d4a384">
    <metadata>
        <timestamp>2022-01-01T00:00:00.000000+00:00</timestamp>
        <tools>
            <tool>
                <vendor>CycloneDX</vendor>
                <name>cyclonedx-python-lib</name>
                <version>2.4.0</version>
                <externalReferences>
                    <reference type="documentation">
                        <url>https://cyclonedx.github.io/cyclonedx-python-lib/</url>
                    </reference>
                    <reference type="license">
                        <url>https://github.com/CycloneDX/cyclonedx-python-lib/blob/main/LICENSE</url>
                    </reference>
                    <reference type="build-system">
                        <url>https://github.com/CycloneDX/cyclonedx-python-lib/actions</url>
                    </reference>
                    <reference type="distribution">
                        <url>https://pypi.org/project/cyclonedx-python-lib/</url>
                    </reference>
                    <reference type="vcs">
                        <url>https://github.com/CycloneDX/cyclonedx-python-lib</url>
                    </reference>
                    <reference type="website">
                        <url>https://cyclonedx.org</url>
                    </reference>
                    <reference type="release-notes">
                        <url>https://github.com/CycloneDX/cyclonedx-python-lib/blob/main/CHANGELOG.md</url>
                    </reference>
                    <reference type="issue-tracker">
                        <url>https://github.com/CycloneDX/cyclonedx-python-lib/issues</url>
                    </reference>
                </externalReferences>
            </tool>
            <tool>
                <vendor>bridgecrew</vendor>
                <name>checkov</name>
                <version>2.0.1124</version>
                <externalReferences>
                    <reference type="website">
                        <url>https://www.checkov.io/</url>
                    </reference>
                    <reference type="license">
                        <url>https://github.com/bridgecrewio/checkov/blob/master/LICENSE</url>
                    </reference>
                    <reference type="social">
                        <url>https://twitter.com/bridgecrewio</url>
                    </reference>
                    <reference type="distribution">
                        <url>https://pypi.org/project/checkov/</url>
                    </reference>
                    <reference type="build-system">
                        <url>https://github.com/bridgecrewio/checkov/actions</url>
                    </reference>
                    <reference type="vcs">
                        <url>https://github.com/bridgecrewio/checkov</url>
                    </reference>
                    <reference type="issue-tracker">
                        <url>https://github.com/bridgecrewio/checkov/issues</url>
                    </reference>
                    <reference type="documentation">
                        <url>https://www.checkov.io/1.Welcome/What%20is%20Checkov.html</url>
                    </reference>
                </externalReferences>
            </tool>
        </tools>
    </metadata>
    <components>
        <component type="file" bom-ref="3281c6f0-43f1-434c-8394-794e467cf08b">
            <name>/main.tf</name>
            <version>0.0.0-75e9492cde2b</version>
            <hashes>
                <hash alg="SHA-1">75e9492cde2b57446170deb28d626fd0dcdc04aa</hash>
            </hashes>
            <purl>pkg:generic/main.tf@0.0.0-75e9492cde2b</purl>
        </component>
    </components>
    <dependencies>
        <dependency ref="3281c6f0-43f1-434c-8394-794e467cf08b"/>
    </dependencies>
    <vulnerabilities>
        <vulnerability bom-ref="5465719a-1c06-4518-acdf-9aab4b4c00a5">
            <id>CKV_AWS_157</id>
            <source>
                <name>checkov</name>
            </source>
            <description>Resource: aws_db_instance.default. Ensure that RDS instances have Multi-AZ enabled
            </description>
            <advisories>
                <advisory>
                    <url>https://docs.bridgecrew.io/docs/general_73</url>
                </advisory>
            </advisories>
        </vulnerability>
        <vulnerability bom-ref="258827d0-cf9d-4aeb-8600-4a192e44f0a7">
            <id>CKV_AWS_16</id>
            <source>
                <name>checkov</name>
            </source>
            <description>Resource: aws_db_instance.default. Ensure all data stored in the RDS is securely encrypted at
                rest
            </description>
            <advisories>
                <advisory>
                    <url>https://docs.bridgecrew.io/docs/general_4</url>
                </advisory>
            </advisories>
        </vulnerability>
    </vulnerabilities>
</bom>
```

The default schema version is currently `v1.4`, but can be adjusted by setting the environment variable `CHECKOV_CYCLONEDX_SCHEMA_VERSION`.

ex.
```shell
CHECKOV_CYCLONEDX_SCHEMA_VERSION=1.3 checkov -d . -o cyclonedx
```
