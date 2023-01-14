# Gitlabci checker

![release](https://img.shields.io/github/v/release/lorenzophys/gitlabci-checker)
[![codecov](https://codecov.io/gh/lorenzophys/gitlabci-checker/branch/main/graph/badge.svg?token=WEZ1UH621Y)](https://codecov.io/gh/lorenzophys/gitlabci-checker)
[![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/lorenzophys/gitlabci-checker/test-workflow.yml?branch=main&label=tests)](https://img.shields.io/github/actions/workflow/status/lorenzophys/gitlabci-checker/test-workflow.yml)
![pver](https://img.shields.io/pypi/pyversions/gitlabci-checker)
![MIT](https://img.shields.io/github/license/lorenzophys/gitlabci-checker)

## Installation

You can install `gitlabci-checker` via `pip`:

```console
user@laptop:~$ pip install gitlabci-checker
```

You can interact with the CLI via the `cicheck` comand:

```console
user@laptop:~$ cicheck
Usage: cicheck [OPTIONS] FILENAME

  Check if your gitlab-ci pipeline compiles correctly.

Options:
  -h, --help                 Show this message and exit.
  -v, --version              Show the version and exit.
  -t, --token TEXT           Your Gitlab access token: by default the content
                             of the GITLAB_TOKEN variable is used.  [required]
  -s, --gitlab-server TEXT   The Gitlab server hostname.  [required]
  -k, --insecure             Use insecure connection (http).
  -w, --warnings-are-errors  Force the failure if warnings are found.
```

## How it works?

`cicheck` just calls the [Gitlab CI lint API](https://docs.gitlab.com/15.7/ee/api/lint.html) with the file you pass to it.

By default it will send the request to `gitlab.com`. If you want to use your own Gitlab instance you must pass the server address:

```console
user@laptop:~$ cicheck .gitlab-ci.yaml --gitlab-server code.company.com
Everything's fine.
```

You must pass a valid token to the CLI: either as the environment variable `GITLAB_TOKEN` or via the `--token` flag.

## Usage example

If your pipeline is valid it returns a "Everything's fine." message

```console
user@laptop:~$ cicheck .gitlab-ci.yaml
Everything's fine.
```

If your configuration is invalid it returns an error message together with the response from Gitlab:

```console
user@laptop:~$ cicheck .gitlab-ci.yaml
Check failed with error(s).
{
  "status": "invalid",
  "errors": [
    "variables config should be a hash of key value pairs"
  ],
  "warnings": []
}
```

You can also force a failure whenever the linter returns a warning by appending `--warnings-are-errors` or `-w`:

```console
user@laptop:~$ cicheck .gitlab-ci.yaml --warnings-are-errors
Check failed with warning(s).
{
  "status": "valid",
  "errors": [],
  "warnings": ["jobs:job may allow multiple pipelines to run for a single action due to
  `rules:when` clause with no `workflow:rules` - read more:
  https://docs.gitlab.com/ee/ci/troubleshooting.html#pipeline-warnings"]
}
```

## `pre-commit` hook

`gitlabci-checker` can be also used as a [pre-commit](https://pre-commit.com) hook. For example:

```yaml
repos:
  - repo: https://github.com/lorenzophys/gitlabci-checker
    rev: v0.1.1
    hooks:
      - id: gitlabci-checker
        args:
          - --gitlab-server code.company.com
          - --warnings-are-errors
```

## License

This project is licensed under the **MIT License** - see the *LICENSE* file for details.
