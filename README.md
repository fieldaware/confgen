[![Build Status](https://travis-ci.org/fieldaware/confgen.svg?branch=master)](https://travis-ci.org/fieldaware/confgen)


# Intro

Configuration generation tool (confgen for short) is designed for operation teams to store and generate configuration files. It often happens that one service is configured differently depending on the environment where it is deployed.

It is highly recommended to use this tool with some configuration management systems such as consul.

# Installation

The list of releases is here: https://github.com/fieldaware/confgen/releases
Each release contains python wheel which can be installed with pip

For example, user wants to install `confgen 0.4.1`:

### Virtualenv installation:
```
pip install https://github.com/fieldaware/confgen/releases/download/0.4.1/confgen-0.4.1-py2.py3-none-any.whl
```


### Global installation:

Do the same thing but with sudo

```
sudo pip install https://github.com/fieldaware/confgen/releases/download/0.4.1/confgen-0.4.1-py2.py3-none-any.whl
```

### Running
After installation you should be able to run:

```
> confgen --help
Usage: confgen [OPTIONS] COMMAND [ARGS]...

Options:
  --ct-home DIRECTORY  The config home - typically your config git repo
  --config FILENAME    Defaults to configtool.yaml in current directory
  --help               Show this message and exit.

Commands:
  build
  delete
  lint
  search
  set
```

# Usage


## confgen.yaml
Each confgen repo needs `confgen.yaml` at the root directory.
From `minimalexample`:

```
examples/minimaldemo > cat confgen.yaml
service: &services
  - app
  - db

infra:
  prod: *services
```

1. `service` section declares services that will be available across our infrastructure. So in our case, `app` and `db`
2. `infra` section declares which services are running on which servers. It can be much more complex, but for for minimal example. We declare only `prod`  with `db` and `app`



## inventory

Inventory is the place where user declares the state for the services. You can add keys and values to the inventory by manually editing `config.yaml` files or by calling `confgen set {KEY} {PATH} {VALUE}`.

This simple structure declares some key/value pairs for both `dev` and `prod` environment.
```
examples/minimaldemo > tree inventory/
inventory/
├── dev
│   └── config.yaml
└── prod
    └── config.yaml

examples/minimaldemo > cat inventory/prod/config.yaml
dburi: mysql://mysql@prod
dbversion: 5.7

examples/minimaldemo > cat inventory/dev/config.yaml
dburi: mysql://mysql@dev
dbversion: 5.8
```

For this configuration we expect prod db to be set for `dbversion = 5.7` and `dburi = mysql://mysql@prod`
You can add some global key/value pairs to global scope of the inventory by calling:

```
examples/minimaldemo > confgen set / version 1.0

examples/minimaldemo > cat inventory/config.yaml
!!python/unicode 'version': !!python/unicode '1.0'
```

Or you can add some key/value pairs to existing inventory files.


```
examples/minimaldemo > confgen set /prod version 1.1

examples/minimaldemo > cat inventory/prod/config.yaml
dburi: mysql://mysql@prod
dbversion: 5.7
!!python/unicode 'version': !!python/unicode '1.1'
```

## templates

Each service declared in `confgen.yaml` (in our case `app` and `db`) needs a set of templates that will be used to render configuration files. In that minimal example we declare only one template per service but you can create many.

Template variables are keys from the inventory that we declared in previous section.

```
examples/minimaldemo > tree templates/
templates/
├── app
│   └── production.ini
└── db
    └── mysql.cnf

examples/minimaldemo > cat templates/app/production.ini
dburi = {{ dburi }}

examples/minimaldemo > cat templates/db/mysql.cnf
dbversion = {{ dbversion }}
```

## build

Build step collects inventory from the file structure and renders templates for declared services.

```
examples/minimaldemo > confgen build

examples/minimaldemo > tree build/
build/
└── prod
    ├── app
    │   └── production.ini
    └── db
        └── mysql.cnf

examples/minimaldemo > cat build/prod/app/production.ini
dburi = mysql://mysql@prod

examples/minimaldemo > cat build/prod/db/mysql.cnf
dbversion = 5.7
```

## set
We can update our inventory by call `set` command in confgen tool. For example, we want to declare key/value pair called `app_name` in global scope - that will be available in both prod and dev scope.

```
examples/minimaldemo > confgen set --help
Usage: confgen set [OPTIONS] PATH KEY VALUE
```

Paths are the same as in file system, so to add `app_name` to global scope we need to add it to `/`.
```
examples/minimaldemo > confgen set / app_name confgen
```

To see the changes we need to adapt one of the templates, for this case let's use `production.ini` for `app` service.

```
examples/minimaldemo > cat templates/app/production.ini
dburi = {{ dburi }}
name = {{ app_name }}
```

## delete

If you want to delete some keys from inventory, use `delete`. Let's delete `app_name`.

```
examples/minimaldemo > confgen delete --help
Usage: confgen delete [OPTIONS] PATH KEY

examples/minimaldemo > confgen delete / app_name
```
