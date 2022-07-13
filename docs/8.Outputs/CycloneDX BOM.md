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
<bom serialNumber="urn:uuid:25c12686-6e25-4e5a-9ec7-d53d609a426e" version="1" xmlns="http://cyclonedx.org/schema/bom/1.4">
  <metadata>
    <timestamp>2022-07-12T17:13:22.461688+00:00</timestamp>
    <tools>
      <tool>
        <vendor>CycloneDX</vendor>
        <name>cyclonedx-python-lib</name>
        <version>2.6.0</version>
        <externalReferences>
          <reference type="build-system">
            <url>https://github.com/CycloneDX/cyclonedx-python-lib/actions</url>
          </reference>
          <reference type="distribution">
            <url>https://pypi.org/project/cyclonedx-python-lib/</url>
          </reference>
          <reference type="documentation">
            <url>https://cyclonedx.github.io/cyclonedx-python-lib/</url>
          </reference>
          <reference type="issue-tracker">
            <url>https://github.com/CycloneDX/cyclonedx-python-lib/issues</url>
          </reference>
          <reference type="license">
            <url>https://github.com/CycloneDX/cyclonedx-python-lib/blob/main/LICENSE</url>
          </reference>
          <reference type="release-notes">
            <url>https://github.com/CycloneDX/cyclonedx-python-lib/blob/main/CHANGELOG.md</url>
          </reference>
          <reference type="vcs">
            <url>https://github.com/CycloneDX/cyclonedx-python-lib</url>
          </reference>
          <reference type="website">
            <url>https://cyclonedx.org</url>
          </reference>
        </externalReferences>
      </tool>
      <tool>
        <vendor>bridgecrew</vendor>
        <name>checkov</name>
        <version>2.1.38</version>
        <externalReferences>
          <reference type="build-system">
            <url>https://github.com/bridgecrewio/checkov/actions</url>
          </reference>
          <reference type="distribution">
            <url>https://pypi.org/project/checkov/</url>
          </reference>
          <reference type="documentation">
            <url>https://www.checkov.io/1.Welcome/What%20is%20Checkov.html</url>
          </reference>
          <reference type="issue-tracker">
            <url>https://github.com/bridgecrewio/checkov/issues</url>
          </reference>
          <reference type="license">
            <url>https://github.com/bridgecrewio/checkov/blob/master/LICENSE</url>
          </reference>
          <reference type="social">
            <url>https://twitter.com/bridgecrewio</url>
          </reference>
          <reference type="vcs">
            <url>https://github.com/bridgecrewio/checkov</url>
          </reference>
          <reference type="website">
            <url>https://www.checkov.io/</url>
          </reference>
        </externalReferences>
      </tool>
    </tools>
  </metadata>
  <components>
    <component bom-ref="pkg:terraform/main.tf/aws_s3_bucket.example@sha1:92911b13224706178dded562c18d281b22bf391a" type="application">
      <name>aws_s3_bucket.example</name>
      <version>sha1:92911b13224706178dded562c18d281b22bf391a</version>
      <hashes>
        <hash alg="SHA-1">92911b13224706178dded562c18d281b22bf391a</hash>
      </hashes>
      <purl>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:92911b13224706178dded562c18d281b22bf391a</purl>
    </component>
  </components>
  <dependencies>
    <dependency ref="pkg:terraform/main.tf/aws_s3_bucket.example@sha1:92911b13224706178dded562c18d281b22bf391a"/>
  </dependencies>
  <vulnerabilities>
    <vulnerability bom-ref="94a37872-6ffb-46ef-9ea7-b5a05199d413">
      <id>CKV2_AWS_6</id>
      <source>
        <name>checkov</name>
      </source>
      <description>Resource: aws_s3_bucket.example. Ensure that S3 bucket has a Public Access block</description>
      <advisories>
        <advisory>
          <url>https://docs.bridgecrew.io/docs/s3-bucket-should-have-public-access-blocks-defaults-to-false-if-the-public-access-block-is-not-attached</url>
        </advisory>
      </advisories>
      <affects>
        <target>
          <ref>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:92911b13224706178dded562c18d281b22bf391a</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="17850edf-25f3-439f-a3ce-243b69d33b7e">
      <id>CKV_AWS_144</id>
      <source>
        <name>checkov</name>
      </source>
      <description>Resource: aws_s3_bucket.example. Ensure that S3 bucket has cross-region replication enabled</description>
      <advisories>
        <advisory>
          <url>https://docs.bridgecrew.io/docs/ensure-that-s3-bucket-has-cross-region-replication-enabled</url>
        </advisory>
      </advisories>
      <affects>
        <target>
          <ref>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:92911b13224706178dded562c18d281b22bf391a</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="13417f16-0808-4d39-a139-32a32368b317">
      <id>CKV_AWS_145</id>
      <source>
        <name>checkov</name>
      </source>
      <description>Resource: aws_s3_bucket.example. Ensure that S3 buckets are encrypted with KMS by default</description>
      <advisories>
        <advisory>
          <url>https://docs.bridgecrew.io/docs/ensure-that-s3-buckets-are-encrypted-with-kms-by-default</url>
        </advisory>
      </advisories>
      <affects>
        <target>
          <ref>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:92911b13224706178dded562c18d281b22bf391a</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="4095ff5b-8eb9-48bf-8c36-01a4f826c91d">
      <id>CKV_AWS_18</id>
      <source>
        <name>checkov</name>
      </source>
      <description>Resource: aws_s3_bucket.example. Ensure the S3 bucket has access logging enabled</description>
      <advisories>
        <advisory>
          <url>https://docs.bridgecrew.io/docs/s3_13-enable-logging</url>
        </advisory>
      </advisories>
      <affects>
        <target>
          <ref>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:92911b13224706178dded562c18d281b22bf391a</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="444525e3-c770-4ee3-b13c-3ebcac5c3394">
      <id>CKV_AWS_19</id>
      <source>
        <name>checkov</name>
      </source>
      <description>Resource: aws_s3_bucket.example. Ensure all data stored in the S3 bucket is securely encrypted at rest</description>
      <advisories>
        <advisory>
          <url>https://docs.bridgecrew.io/docs/s3_14-data-encrypted-at-rest</url>
        </advisory>
      </advisories>
      <affects>
        <target>
          <ref>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:92911b13224706178dded562c18d281b22bf391a</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="9e02a653-d6da-4454-ac0a-08fcdc172995">
      <id>CKV_AWS_21</id>
      <source>
        <name>checkov</name>
      </source>
      <description>Resource: aws_s3_bucket.example. Ensure all data stored in the S3 bucket have versioning enabled</description>
      <advisories>
        <advisory>
          <url>https://docs.bridgecrew.io/docs/s3_16-enable-versioning</url>
        </advisory>
      </advisories>
      <affects>
        <target>
          <ref>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:92911b13224706178dded562c18d281b22bf391a</ref>
        </target>
      </affects>
    </vulnerability>
  </vulnerabilities>
</bom>
```

The default schema version is currently `v1.4`, but can be adjusted by setting the environment variable `CHECKOV_CYCLONEDX_SCHEMA_VERSION`.

ex.
```shell
CHECKOV_CYCLONEDX_SCHEMA_VERSION=1.3 checkov -d . -o cyclonedx
```
