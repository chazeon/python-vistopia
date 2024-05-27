import json
import logging
from logging import getLogger
from typing import Optional

import click
from tabulate import tabulate
from os import environ

from .visitor import Visitor
from .utils import range_expand

logger = getLogger(__name__)


class Context:
    def __init__(self):
        self.token: Optional[str] = None
        self.visitor: Optional[Visitor] = None


# def _print_table(list):
#     table = tabulate()
#     click.echo(table)


@click.group()
@click.option("-t", "--token", help="API token.")
@click.option("-v", "--verbosity", default="INFO", help="Logging level.")
@click.pass_context
def main(ctx, **argv):

    verbosity = argv.pop("verbosity").upper()
    logging.basicConfig(format='%(asctime)s %(message)s', level=verbosity)

    token = environ.get("VISTOPIA_API_TOKEN", None)
    token = argv.get("token", None) or token
    logger.debug(f"API token `{token}` received.")

    ctx.obj = Context()
    ctx.obj.visitor = Visitor(token=token)


@main.command("search")
@click.option("--keyword", "-k", type=click.STRING, required=True,
              help="Search keyword.")
@click.pass_context
def search(ctx, **argv):
    visitor: Visitor = ctx.obj.visitor
    search_result_list = visitor.search(argv.pop("keyword"))
    logger.debug(json.dumps(search_result_list, indent=2, ensure_ascii=False))

    table = []
    for item in search_result_list:
        if item["data_type"] != "content":
            continue
        author = item["author"]
        if item["subtitle"]:
            title = "%s: %s" % ([item['title'], item['subtitle']])
        else:
            title = item['title']
        desc = item['share_desc']
        content_id = item['id']
        table.append((content_id, author, title, desc))

    click.echo(tabulate(table))


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
    logger.debug(json.dumps(
        visitor.get_catalog(content_id), indent=2, ensure_ascii=False))

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
@click.option("--no-tag", is_flag=True, default=False,
              help="Do not add IDv3 tags.")
@click.option("--episode-id", help="Episode ID in the form '1-3,4,8'")
@click.pass_context
def save_show(ctx, **argv):
    content_id = argv.pop("id")
    episode_id = argv.pop("episode_id", None)
    episodes = set(range_expand(episode_id) if episode_id else [])

    logger.debug(json.dumps(
        ctx.obj.visitor.get_catalog(content_id), indent=2, ensure_ascii=False))

    ctx.obj.visitor.save_show(
        content_id,
        no_tag=argv.pop("no_tag"),
        episodes=episodes,
    )


@main.command("save-transcript")
@click.option("--id", type=click.INT, required=True)
@click.option("--episode-id", help="Episode ID in the form '1-3,4,8'")
@click.pass_context
def save_transcript(ctx, **argv):
    content_id = argv.pop("id")
    episode_id = argv.pop("episode_id", None)
    episodes = set(range_expand(episode_id) if episode_id else [])

    logger.debug(json.dumps(
        ctx.obj.visitor.get_catalog(content_id), indent=2, ensure_ascii=False))

    ctx.obj.visitor.save_transcript(
        content_id,
        episodes=episodes
    )


if __name__ == "__main__":
    main()
