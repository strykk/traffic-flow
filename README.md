# Traffic flow simulation

## Setup

The project uses `poetry` as dependency management tool. Install it using the instructions [on the website](https://python-poetry.org/).
Then, the following command installs all the project's dependencies:

```bash
poetry install
```

To activate `poetry` virtial environment and start shell within it, run

```bash
poetry shell
```

Then you can simply run all the project's commands. Mind, that if you do not activate the `poetry` shell, you'll need to prefix all the commands with `poetry run`. For example:

```bash
poetry run pre-commit run --all-files
```

In other parts of the document it is assumed that the commands are run from the shell in the virtual env and skip the prefix, e.g.

```bash
pre-commit run --all-files
```

## Development

### `pre-commit`

The project uses `pre-commit` to keep the code well-formatted. You can install it with the following command:

```bash
pre-commit install
```
