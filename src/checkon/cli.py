import pathlib

import click
import tabulate

import checkon.results

from . import app


def run_cli(urls_lists, hide_passed, **kw):
    urls = [url for urls in urls_lists for url in urls]

    print(app.run_many(project_urls=urls, **kw))


def compare_cli(urls_lists, hide_passed, output_format, **kw):
    urls = [url for urls in urls_lists for url in urls]
    records = checkon.app.compare(project_urls=urls, **kw)
    if hide_passed:
        records = [r for r in records if r["text"] is not None]

    import json

    if output_format == "json":
        print(json.dumps(records))
    elif output_format == "table":
        print(tabulate.tabulate(records, headers="keys"))

    else:
        raise ValueError(output_format)


def read_from_file(file):
    return [line.strip() for line in file.readlines()]


dependents = [
    click.Command(
        "dependents-from-librariesio",
        params=[
            click.Argument(["pypi-name"]),
            click.Option(
                ["--api-key"],
                required=True,
                envvar="CHECKON_LIBRARIESIO_API_KEY",
                help="libraries.io API key",
            ),
            click.Option(
                ["--limit"],
                type=int,
                help="Maximum number of dependents to find.",
                default=5,
                show_default=True,
            ),
        ],
        callback=app.get_dependents,
        help="Get dependent projects on PyPI, via https://libraries.io API",
    ),
    click.Command(
        "dependents-from-file",
        params=[click.Argument(["file"], type=click.File())],
        help="List dependent project urls in a file, line-separated.",
        callback=read_from_file,
    ),
    click.Command(
        "dependents",
        params=[click.Argument(["dependents"], nargs=-1, required=True)],
        callback=lambda dependents: list(dependents),
        help="List dependent project urls on the command line.",
    ),
]


hide_passed = click.Option(
    ["--hide-passed"], is_flag=True, help="Whether to hide tests that passed."
)


test = click.Group(
    "test",
    commands={c.name: c for c in dependents},
    params=[
        click.Option(["--inject"], help="Depdendency version(s).", multiple=True),
        hide_passed,
        click.Option(
            ["--output-format"],
            type=click.Choice(["json", "table"]),
            default="table",
            help="Output format",
        ),
    ],
    result_callback=compare_cli,
    chain=True,
    help="Compare multiple versions of a depdendency on their depdendents tests.",
)

list_commands = click.Group(
    "list",
    commands={c.name: c for c in dependents},
    result_callback=lambda x: print("\n".join(x)),
    help="List dependent libraries of a depdendency.",
)
cli = click.Group(
    "run",
    commands={"list": list_commands, "test": test},
    help="Run tests of dependent packages using different versions of a depdendency library.",
)
