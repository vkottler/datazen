<!--
    =====================================
    generator=datazen
    version=1.7.9
    hash=dd544728d64208885eea4f71be4b3028
    =====================================
-->

# datazen ([1.7.10](https://pypi.org/project/datazen/))

[![python](https://img.shields.io/pypi/pyversions/datazen.svg)](https://pypi.org/project/datazen/)
![Build Status](https://github.com/vkottler/datazen/workflows/Python%20package/badge.svg)
[![codecov](https://codecov.io/gh/vkottler/datazen/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/github/vkottler/datazen)

*Compile and render schema-validated configuration data.*

Good software is composable and configurable, but
the complexity of managing configuration data scales with its complexity.

This package simplifies data curation and partitioning for uses in rendering
templates, or just rendering final sets of serialized data.

# Usage

```
$ ./venv3.8/bin/dz -h

usage: dz [-h] [--version] [-v] [-C DIR] [-m MANIFEST] [-c] [--sync] [-d]
          [targets [targets ...]]

Compile and render schema-validated configuration data.

positional arguments:
  targets               target(s) to execute

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -v, --verbose         set to increase logging verbosity
  -C DIR, --dir DIR     execute from a specific directory
  -m MANIFEST, --manifest MANIFEST
                        manifest to execute tasks from (default:
                        'manifest.yaml')
  -c, --clean           clean the manifest's cache and exit
  --sync                sync the manifest's cache (write-through) with the
                        state of the file system before execution
  -d, --describe        describe the manifest's cache and exit

```

# Manifest Schema

A manifest is provided to `datazen` to establish the set of targets
that should be executed based on defaults or the command-line invocation.

## Manifest Includes

Include additional files to build the final, root manifest with.
This same schema applies to included files.


```
includes: paths
```
## Output Directory

Override the default output directory (i.e. `datazen-out`).

```
output_dir:
  type: string
```
## Cache Directory

Override the default cache directory (i.e. `.manifest_cache`).

```
cache_dir:
  type: string
```
## Global Loads

For each of these keys, add paths that should be loaded globally.

```
configs:      paths
schemas:      paths
schema_types: paths
templates:    paths
variables:    paths
```
## Manifest Parameters

Manifests themselves are
[Jinja](https://jinja.palletsprojects.com/en/2.11.x/) templates that are
rendered with the data contained in this key.


```
params:
  type: dict
```
## Default Target

The target to execute by default if none is provided.

```
default_target:
  type: string
```
## Compiles

Target definitions for compilation tasks.

```
compiles:
  type: list
  schema:
    type: dict
    schema:
      configs: paths
      schemas: paths
      variables: paths
      dependencies: deps
      name:
        type: string
      override_path:
        type: string
      output_type:
        type: string
      output_dir:
        type: string
      index_path:
        type: string
      append:
        type: boolean
```
## Commands

Target definitions for command-line command tasks.

```
commands:
  type: list
  schema:
    type: dict
    schema:
      file:
        type: string
      name:
        type: string
      command:
        type: string
      force:
        type: boolean
      arguments: deps
      dependencies: deps
```
## Renders

Target definitions for render tasks. Renders can create output files based
on [Jinja](https://jinja.palletsprojects.com/en/2.11.x/) templates, or just
String data to be used as a dependency for another task.


```
renders:
  type: list
  schema:
    type: dict
    schema:
      templates: paths
      children: deps
      child_delimeter:
        type: string
      child_indent:
        type: integer
      dependencies: deps
      name:
        type: string
      override_path:
        type: string
      as:
        type: string
      key:
        type: string
      output_dir:
        type: string
      output_path:
        type: string
      no_dynamic_fingerprint:
        type: boolean
      no_file:
        type: boolean
      indent:
        type: integer
```
## Groups

Target definitions for group tasks. Groups declare a set of dependencies
and nothing else. Groups can be used as dependencies for any other target.


```
groups:
  type: list
  schema:
    type: dict
    schema:
      name:
        type: string
      dependencies: deps
```

# Manifest Schema Types

These items may appear in the manifest schema.

## deps

Dependencies are lists of Strings.
They should be formatted as `(compiles,renders,...)-target`.


```
type: list
schema:
  type: string
```
## paths

Paths are lists of Strings and can use `/` or `\\` as delimeters.
Paths are relative to the directory that a manifest file is in, but for
manifest includes, all "loaded" directories are relative to the root
manifest's directory. Paths can also be absolute.


```
type: list
schema:
  type: string
```

This entire document is generated by this package.
