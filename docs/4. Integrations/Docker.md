---
title: "Docker"
slug: "docker"
hidden: false
createdAt: "2021-03-22T15:29:46.762Z"
updatedAt: "2021-03-22T16:10:18.384Z"
---
#Using Checkov with Docker
[block:code]
{
  "codes": [
    {
      "code": "docker pull bridgecrew/checkov\ndocker run --tty --volume /user/tf:/tf bridgecrew/checkov --directory /tf\n",
      "language": "coffeescript",
      "name": " "
    }
  ]
}
[/block]

[block:callout]
{
  "type": "info",
  "title": "Notes",
  "body": "If you are using Python 3.6 (which is the default version in Ubuntu 18.04) Checkov will not work and it will fail with `ModuleNotFoundError: No module named 'dataclasses'`. In this case, you can use the Docker version instead.\n\nIn certain cases, when redirecting `docker run --tty` output to a file - for example, if you want to save the Checkov JUnit output to a file - will cause extra control characters to be printed. This can break file parsing. If you encounter this, remove the --tty flag."
}
[/block]