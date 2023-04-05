import click
import json
import logging
from logging import getLogger
from pprint import pprint
from visitor import Visitor
from tabulate import tabulate


logger = getLogger(__name__)


class Context:
    def __init__(self):
        self.token: str = None
        self.visitor: Visitor = None

# def _print_table(list):
#     table = tabulate()
#     click.echo(table)

@click.group()
@click.option("-t", "--token", help="API token")
@click.option("-v", "--verbosity", default="INFO", help="Logging level")
@click.pass_context
def main(ctx, **argv):


    verbosity = argv.pop("verbosity").upper()
    logging.basicConfig(format='%(asctime)s %(message)s', level=verbosity)

    token = argv.pop("token", None)

    ctx.obj = Context()
    ctx.obj.visitor = Visitor(token=token)


@main.command("subscriptions")
@click.pass_context
def subscriptions(ctx):

    visitor: Visitor = ctx.obj.visitor

    logger.debug(visitor.get_user_subscriptions_list())

    table = []
    for show in visitor.get_user_subscriptions_list():
        title = ": ".join([show['title'], show['subtitle']])
        content_id = show["content_id"]
        table.append((content_id, title))

    click.echo(tabulate(table))


@main.command("show-content")
@click.option("--id", type=click.INT, required=True)
@click.pass_context
def show_content(ctx, **argv):

    visitor: Visitor = ctx.obj.visitor

    content_id = argv.pop("id")
    logger.debug(visitor.get_content_show(content_id))
    logger.debug(json.dumps(visitor.get_catalog(content_id), indent=2, ensure_ascii=False))

    table = []
    catalog = visitor.get_catalog(content_id)
    for part in catalog["catalog"]:
        for article in part["part"]:
            table.append((
                article["sort_number"],
                # article["article_id"],
                article["title"],
                article["duration_str"],
            ))

    click.echo(tabulate(table))



@main.command("save-show")
@click.option("--id", type=click.INT, required=True)
@click.option("--no-tag", is_flag=True, default=False, help="Do not add IDv3 tags.")
@click.pass_context
def save_show(ctx, **argv):

    content_id = argv.pop("id")
    logger.debug(json.dumps(ctx.obj.visitor.get_catalog(content_id), indent=2, ensure_ascii=False))

    ctx.obj.visitor.save_show(content_id, argv.pop("no_tag"))


@main.command("save-transcript")
@click.option("--id", type=click.INT, required=True)
@click.pass_context
def save_transcript(ctx, **argv):

    content_id = argv.pop("id")
    logger.debug(json.dumps(ctx.obj.visitor.get_catalog(content_id), indent=2, ensure_ascii=False))

    ctx.obj.visitor.save_transcript(content_id)


if __name__ == "__main__":
    main()