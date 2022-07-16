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
<bom xmlns="http://cyclonedx.org/schema/bom/1.4" serialNumber="urn:uuid:4d32cfec-d0dc-4e92-bf71-4c92cf37c3ed" version="1">
  <metadata>
    <timestamp>2022-07-16T17:57:47.032316+00:00</timestamp>
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
    <component bom-ref="pkg:terraform/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85" type="application">
      <name>aws_s3_bucket.example</name>
      <version>sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</version>
      <hashes>
        <hash alg="SHA-1">c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</hash>
      </hashes>
      <purl>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</purl>
    </component>
    <component bom-ref="pkg:pypi/flask@0.6" type="library">
      <name>flask</name>
      <version>0.6</version>
      <purl>pkg:pypi/flask@0.6</purl>
    </component>
  </components>
  <dependencies>
    <dependency ref="pkg:terraform/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85" />
    <dependency ref="pkg:pypi/flask@0.6" />
  </dependencies>
  <vulnerabilities>
    <vulnerability bom-ref="66fa9728-fb5e-42ed-9077-ef5891c78b5a">
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
          <ref>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="48f2e69c-7536-47ae-b7d5-05bb2373b99e">
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
          <ref>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="977dd771-0613-4c75-9c3d-8e675ed699eb">
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
          <ref>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="63996fcf-3596-4cae-8a68-8a42ad1b853f">
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
          <ref>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="ba95bf88-b448-4a2b-aec5-0520df32f05e">
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
          <ref>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="41f657e7-a83b-4535-9b83-541211d02397">
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
          <ref>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="5b200cf7-f0c2-42b8-87a8-8c73b90de39f">
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
          <ref>pkg:pypi/flask@0.6</ref>
        </target>
      </affects>
    </vulnerability>
    <vulnerability bom-ref="f18f3674-092f-4e9a-8452-641fd11fc70f">
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
          <ref>pkg:pypi/flask@0.6</ref>
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

## Structure

Further information on the different elements and attributes can be found [here](https://cyclonedx.org/docs/1.4/xml/).

### component

Each component stores the information of a single IaC resource or SCA package.

IaC
```xml
<component bom-ref="pkg:terraform/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85" type="application">
  <name>aws_s3_bucket.example</name>
  <version>sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</version>
  <hashes>
    <hash alg="SHA-1">c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</hash>
  </hashes>
  <purl>pkg:terraform/main.tf/aws_s3_bucket.example@sha1:c9b9b2eba0a7d4ccb66096df77e1a6715ea1ae85</purl>
</component>
```

- `name`: Resource ID
- `version`: sha1 hash of the file
- `hash`: sha1 hash of the file
- `purl`: Format `pkg:<runner name>/<file path>/<resource ID>@<sha1 hash of the file>`

SCA
```xml
<component bom-ref="pkg:pypi/flask@0.6" type="library">
  <name>flask</name>
  <version>0.6</version>
  <purl>pkg:pypi/flask@0.6</purl>
</component>
```

- `group`: Group name of the package
- `name`: Name of the package
- `version`: Version of the package
- `purl`: Format `pkg:<package type>/<package group name>/<packge name>@<package version>`
