---
layout: default
published: true
title: Docker
nav_order: 7
---

# Using Checkov with Docker

```coffeescript
docker pull bridgecrew/checkov
docker run --tty --volume /user/tf:/tf bridgecrew/checkov --directory /tf
```

If you are using Python 3.6 (which is the default version in Ubuntu 18.04) Checkov will not work and it will fail with `ModuleNotFoundError: No module named 'dataclasses'`. In this case, you can use the Docker version instead.\n\nIn certain cases, when redirecting `docker run --tty` output to a file - for example, if you want to save the Checkov JUnit output to a file - will cause extra control characters to be printed. This can break file parsing. If you encounter this, remove the --tty flag.
