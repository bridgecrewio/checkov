# Concepts

## Plan Parser

A component that breaks down the main.tf file into individual infrastructure blocks and translates them into a Python-readable data model. Each block and its configuration values are parsed into a standard schema.



## Dependency Graph

Some infrastructure block classes refer to variables that are stored in separate files. For this reason we created a simple code dependency graph that identifies variable annotations, searches for them in the entire library and adds a logical reference back to it.



## Resource Policy

Every block is inspected and based on the supported resource types it contains, it will get scanned for the related policies. When a match is identified between an unwanted policy and a current configuration, the resource policy will log the filename, line and block ID. 



## Suppressions

Like any static-analysis tool it is limited by its analysis scope. For example, if a resource is managed manually, or using subsequent configuration management tooling, a suppression can be inserted as a simple code annotation.
