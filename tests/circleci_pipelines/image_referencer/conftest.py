from __future__ import annotations
import pytest

from checkov.common.images.image_referencer import Image


@pytest.fixture
def file_path() -> str:
	return ".circleci/config.yml"


@pytest.fixture
def circleci_config_with_images_definitions(file_path) -> dict:
	return {
		file_path: {
			"orbs": {
				"new-orb": "whatever/orbname@goodorb",
				"some-orb": "orbs/orbname@dev:blah",
				"__startline__": 6,
				"__endline__": 9
			},
			"executors": {
				"default-executor": {
					"machine": {
						"image": "windows-server-2022",
						"__startline__": 12,
						"__endline__": 14
					},
					"__startline__": 11,
					"__endline__": 14
				},
				"image-executor": {
					"docker": {
						"image": "mongo:2.6.8",
						"__startline__": 16,
						"__endline__": 18
					},
					"__startline__": 15,
					"__endline__": 18
				},
				"__startline__": 10,
				"__endline__": 18
			},
			"jobs": {
				"test-docker-versioned-img": {
					"docker": [
						{
							"image": "mongo:2.6.8",
							"__startline__": 21,
							"__endline__": 22
						}
					],
					"steps": [
						"some-step"
					],
					"__startline__": 20,
					"__endline__": 25
				},
				"__startline__": 19,
				"__endline__": 25
			},
			"__startline__": 5,
			"__endline__": 25
		}
	}


@pytest.fixture
def circle_ci_filepath_workflow_with_images_config(circleci_config_with_images_definitions, file_path) \
		-> tuple[str, dict]:
	return file_path, circleci_config_with_images_definitions.get(file_path)


@pytest.fixture
def circleci_config_no_images_definitions(file_path) -> dict:
	return {
		file_path: {
			"orbs": {
				"new-orb": "whatever/orbname@goodorb",
				"some-orb": "orbs/orbname@dev:blah",
				"__startline__": 6,
				"__endline__": 9
			},
			"executors": {
				"default-executor": {
					"machine": {
						"image": "windows-server-2022",
						"__startline__": 12,
						"__endline__": 14
					},
					"__startline__": 11,
					"__endline__": 14
				},
				"__startline__": 10,
				"__endline__": 14
			},
			"jobs": {
				"test-macos-image": {
					"macos": {
						"xcode": "9.4.1",
						"__startline__": 17,
						"__endline__": 18
					},
					"steps": [
						"some-step"
					],
					"__startline__": 16,
					"__endline__": 21
				},
				"test-machine-default": {
					"executor": {
						"name": "win/default-executor",
						"__startline__": 23,
						"__endline__": 24
					},
					"steps": [
						"some-step"
					],
					"__startline__": 22,
					"__endline__": 27
				},
				"__startline__": 15,
				"__endline__": 27
			},
			"__startline__": 5,
			"__endline__": 27
		}
	}


@pytest.fixture
def circle_ci_filepath_workflow_no_images_config(circleci_config_no_images_definitions, file_path) -> tuple[str, dict]:
	return file_path, circleci_config_no_images_definitions.get(file_path)


@pytest.fixture
def circle_ci_image1(file_path) -> Image:
	image = Image(
		end_line=18,
		start_line=16,
		name='mongo:2.6.8',
		file_path=file_path,
		related_resource_id='executors(image-executor).docker.image[1](mongo:2.6.8)',
	)
	return image


@pytest.fixture
def circle_ci_image2(file_path) -> Image:
	image = Image(
		end_line=22,
		start_line=21,
		name='mongo:2.6.8',
		file_path=file_path,
		related_resource_id='jobs(test-docker-versioned-img).docker.image[1](mongo:2.6.8)',
	)
	return image


@pytest.fixture
def image_cached_result() -> dict:
	return {
		"results": [
			{
				"id": "sha256:9dbc24674f25eb449df11179ed3717c47348fb3aa985ae14b3936d54c2c09dde",
				"name": "postgres:14.2",
				"distro": "Debian GNU/Linux 11 (bullseye)",
				"distroRelease": "bullseye",
				"digest": "sha256:2c954f8c5d03da58f8b82645b783b56c1135df17e650b186b296fa1bb71f9cfd",
				"collections": [
					"All"
				],
				"packages": [
					{
						"type": "os",
						"name": "base-files",
						"version": "11.1+deb11u3",
						"licenses": [
							"GPL"
						]
					}
				],
				"compliances": [],
				"complianceDistribution": {
					"critical": 0,
					"high": 2,
					"medium": 0,
					"low": 0,
					"total": 2
				},
				"complianceScanPassed": True,
				"vulnerabilities": [
				],
				"vulnerabilityDistribution": {
					"critical": 9,
					"high": 26,
					"medium": 8,
					"low": 17,
					"total": 60
				},
				"vulnerabilityScanPassed": True
			}
		]
	}


@pytest.fixture
def image_cached_results_for_report() -> tuple:
	return (
		{
			'image_name': 'redis@sha256:54057dd7e125ca41afe526a877e8bd35ec2cdd33b9217e022ed37bdcf7d09673',
			'related_resource_id': 'jobs(test-docker-hash-img).docker.image[1](redis@sha256:54057dd7e125ca41afe526a877e8bd35ec2cdd33b9217e022ed37bdcf7d09673)',
			'packages': [{'type': 'os', 'name': 'base-files', 'version': '11.1+deb11u3', 'licenses': ['GPL']}]
		},
		{
			'image_name': 'buildpack-deps:latest',
			'related_resource_id': 'jobs(test-docker-latest-img).docker.image[1](buildpack-deps:latest)',
			'packages': [{'type': 'os', 'name': 'base-files', 'version': '11.1+deb11u3', 'licenses': ['GPL']}]
		},
		{
			'image_name': 'mongo:2.6.8',
			'related_resource_id': 'jobs(test-docker-versioned-img).docker.image[1](mongo:2.6.8)',
			'packages': [{'type': 'os', 'name': 'base-files', 'version': '11.1+deb11u3', 'licenses': ['GPL']}]
		},
		{
			'image_name': 'postgres:14.2',
			'related_resource_id': 'jobs(test-docker-versioned-img).docker.image[2](postgres:14.2)',
			'packages': [{'type': 'os', 'name': 'base-files', 'version': '11.1+deb11u3', 'licenses': ['GPL']}]
		},
		{
			'image_name': 'cimg/python:latest',
			'related_resource_id': 'jobs(test-echo).docker.image[1](cimg/python:latest)',
			'packages': [{'type': 'os', 'name': 'base-files', 'version': '11.1+deb11u3', 'licenses': ['GPL']}]
		},
		{
			'image_name': 'cimg/python:latest',
			'related_resource_id': 'jobs(test-inject).docker.image[1](cimg/python:latest)',
			'packages': [{'type': 'os', 'name': 'base-files', 'version': '11.1+deb11u3', 'licenses': ['GPL']}]
		},
		{
			'image_name': 'cimg/python:latest',
			'related_resource_id': 'jobs(test-inject2).docker.image[1](cimg/python:latest)',
			'packages': [{'type': 'os', 'name': 'base-files', 'version': '11.1+deb11u3', 'licenses': ['GPL']}]
		},
		{
			'image_name': 'cimg/python:latest',
			'related_resource_id': 'jobs(test-curl-secret).docker.image[1](cimg/python:latest)',
			'packages': [{'type': 'os', 'name': 'base-files', 'version': '11.1+deb11u3', 'licenses': ['GPL']}]
		},
		{
			'image_name': 'cimg/python:latest',
			'related_resource_id': 'jobs(test-inject-ci-vars).docker.image[1](cimg/python:latest)',
			'packages': [{'type': 'os', 'name': 'base-files', 'version': '11.1+deb11u3', 'licenses': ['GPL']}]
		},
		{
			'image_name': 'mongo:2.6.8',
			'related_resource_id': 'executors(image-executor).docker.image[1](mongo:2.6.8)',
			'packages': [{'type': 'os', 'name': 'base-files', 'version': '11.1+deb11u3', 'licenses': ['GPL']}]
		}
	)
