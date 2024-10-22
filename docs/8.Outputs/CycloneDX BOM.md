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
<bom xmlns="http://cyclonedx.org/schema/bom/1.4" serialNumber="urn:uuid:59fccc63-7218-4396-befc-5de315c08434" version="1">
  <metadata>
    <timestamp>2022-07-17T14:13:26.536352+00:00</timestamp>
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
        <vendor>prisma_cloud</vendor>
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
            <url>https://twitter.com/prisma_cloud</url>
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
    <component bom-ref="pkg:terraform/cli_repo/pd/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85" type="application">
      <name>aws_s3_bucket.example</name>
      <version>sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</version>
      <hashes>
        <hash alg="SHA-1">c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</hash>
      </hashes>
      <purl>pkg:terraform/cli_repo/pd/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</purl>
    </component>
    <component bom-ref="pkg:pypi/cli_repo/pd/requirements.txt/flask@0.6" type="library">
      <name>flask</name>
      <version>0.6</version>
      <purl>pkg:pypi/cli_repo/pd/requirements.txt/flask@0.6</purl>
    </component>
  </components>
  <dependencies>
    <dependency ref="pkg:terraform/cli_repo/pd/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85" />
    <dependency ref="pkg:pypi/cli_repo/pd/requirements.txt/flask@0.6" />
  </dependencies>
  <vulnerabilities>
    <vulnerability bom-ref="6541a13d-8e97-419d-aaca-7fd185f052fd">
      <id>CKV2_AWS_6</id>
      <source>
        <name>checkov</name>
      </source>
      <description>Resource: aws_s3_bucket.example. Ensure that S3 bucket has a Public Access block</description>
      <advisories>
        <advisory>
          <url>https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3-bucket-should-have-public-access-blocks-defaults-to-false-if-the-public-access-block-is-not-attached</url>
        </advisory>
      </advisories>
      <affects>
        <target>
          <ref>pkg:terraform/cli_repo/pd/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="0b326d31-d730-43d2-9dbf-e898c24d92b5">
      <id>CKV_AWS_144</id>
      <source>
        <name>checkov</name>
      </source>
      <description>Resource: aws_s3_bucket.example. Ensure that S3 bucket has cross-region replication enabled</description>
      <advisories>
        <advisory>
          <url>https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/ensure-that-s3-bucket-has-cross-region-replication-enabled</url>
        </advisory>
      </advisories>
      <affects>
        <target>
          <ref>pkg:terraform/cli_repo/pd/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="fd5b3e13-407b-4af3-a25c-bee3613a7bd8">
      <id>CKV_AWS_145</id>
      <source>
        <name>checkov</name>
      </source>
      <description>Resource: aws_s3_bucket.example. Ensure that S3 buckets are encrypted with KMS by default</description>
      <advisories>
        <advisory>
          <url>https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/ensure-that-s3-buckets-are-encrypted-with-kms-by-default</url>
        </advisory>
      </advisories>
      <affects>
        <target>
          <ref>pkg:terraform/cli_repo/pd/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="df6af40a-3042-4852-8029-87366fbb49ff">
      <id>CKV_AWS_18</id>
      <source>
        <name>checkov</name>
      </source>
      <description>Resource: aws_s3_bucket.example. Ensure the S3 bucket has access logging enabled</description>
      <advisories>
        <advisory>
          <url>https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3_13-enable-logging</url>
        </advisory>
      </advisories>
      <affects>
        <target>
          <ref>pkg:terraform/cli_repo/pd/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="36a44192-ccbb-4534-a8ad-5be689279e3e">
      <id>CKV_AWS_19</id>
      <source>
        <name>checkov</name>
      </source>
      <description>Resource: aws_s3_bucket.example. Ensure all data stored in the S3 bucket is securely encrypted at rest</description>
      <advisories>
        <advisory>
          <url>https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3_14-data-encrypted-at-rest</url>
        </advisory>
      </advisories>
      <affects>
        <target>
          <ref>pkg:terraform/cli_repo/pd/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="43ddb9d1-06d2-4ea5-b112-a2f97a3c03d4">
      <id>CKV_AWS_21</id>
      <source>
        <name>checkov</name>
      </source>
      <description>Resource: aws_s3_bucket.example. Ensure all data stored in the S3 bucket have versioning enabled</description>
      <advisories>
        <advisory>
          <url>https://docs.prismacloud.io/en/enterprise-edition/policy-reference/aws-policies/s3-policies/s3_16-enable-versioning</url>
        </advisory>
      </advisories>
      <affects>
        <target>
          <ref>pkg:terraform/cli_repo/pd/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="8ce0817a-fe7f-48b4-bb43-8c28396a386f">
      <id>CVE-2018-1000656</id>
      <source>
        <url>https://nvd.nist.gov/vuln/detail/CVE-2018-1000656</url>
      </source>
      <ratings>
        <rating>
          <source>
            <url>https://nvd.nist.gov/vuln/detail/CVE-2018-1000656</url>
          </source>
          <score>7.5</score>
          <severity>unknown</severity>
          <method>CVSSv3</method>
          <vector>AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H</vector>
        </rating>
      </ratings>
      <description>The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3. NOTE: this may overlap CVE-2019-1010083.</description>
      <recommendation>fixed in 0.12.3</recommendation>
      <published>2018-08-20T19:31:00</published>
      <affects>
        <target>
          <ref>pkg:pypi/cli_repo/pd/requirements.txt/flask@0.6</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="30c1c64b-d902-4f20-b830-c8a2e6bdc13b">
      <id>CVE-2019-1010083</id>
      <source>
        <url>https://nvd.nist.gov/vuln/detail/CVE-2019-1010083</url>
      </source>
      <ratings>
        <rating>
          <source>
            <url>https://nvd.nist.gov/vuln/detail/CVE-2019-1010083</url>
          </source>
          <score>7.5</score>
          <severity>unknown</severity>
          <method>CVSSv3</method>
          <vector>AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H</vector>
        </rating>
      </ratings>
      <description>The Pallets Project Flask before 1.0 is affected by: unexpected memory usage. The impact is: denial of service. The attack vector is: crafted encoded JSON data. The fixed version is: 1. NOTE: this may overlap CVE-2018-1000656.</description>
      <recommendation>fixed in 1.0</recommendation>
      <published>2019-07-17T14:15:00</published>
      <affects>
        <target>
          <ref>pkg:pypi/cli_repo/pd/requirements.txt/flask@0.6</ref>
        </target>
      </affects>
    </vulnerability>
  </vulnerabilities>
</bom>
```

The output can be either created in a XML

```shell
checkov -d . -o cyclonedx
```

or JSON format.

```shell
checkov -d . -o cyclonedx_json
```

The default schema version is currently `v1.4`, but can be adjusted by setting the environment variable `CHECKOV_CYCLONEDX_SCHEMA_VERSION`.

ex.
```shell
CHECKOV_CYCLONEDX_SCHEMA_VERSION=1.3 checkov -d . -o cyclonedx
```

## Structure

Further information on the different elements and attributes can be found [here](https://cyclonedx.org/docs/1.4/xml/).

### component

Each component stores the information of a single IaC resource or SCA package.

IaC
```xml
<component bom-ref="pkg:terraform/cli_repo/pd/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85" type="application">
  <name>aws_s3_bucket.example</name>
  <version>sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</version>
  <hashes>
    <hash alg="SHA-1">c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</hash>
  </hashes>
  <purl>pkg:terraform/cli_repo/pd/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</purl>
</component>
```

- `name`: Resource ID
- `version`: sha1 hash of the file
- `hash`: sha1 hash of the file
- `purl`: Format `pkg:<runner name>/<repo ID>/<file path>/<resource ID>@<sha1 hash of the file>`

SCA
```xml
<component bom-ref="pkg:pypi/cli_repo/pd/requirements.txt/flask@0.6" type="library">
  <name>flask</name>
  <version>0.6</version>
  <purl>pkg:pypi/cli_repo/pd/requirements.txt/flask@0.6</purl>
</component>
```

- `group`: Group name of the package (only relevant for Maven packages)
- `name`: Name of the package
- `version`: Version of the package
- `purl`: Format `pkg:<package type>/<repo ID>/<file path>/<package group name>/<packge name>@<package version>`

The repo ID will be automatically set depending on the environment `checkov` is invoked in, but can be adjusted by setting the flag `--repo-id`.

ex.
```shell
checkov -d . --repo-id acme/example -o cyclonedx
```
