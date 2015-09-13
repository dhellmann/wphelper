import logging

from wphelper.cmds import base

import markdown
from wordpress_xmlrpc import WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost


class Create(base.WithCredentials):
    "create a new post"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)
        parser.add_argument(
            '--encoding',
            default='utf-8',
            help='file text encoding, defaults to %(default)s',
        )
        parser.add_argument(
            '-t', '--title',
            help='the post title',
        )
        parser.add_argument(
            '-s', '--status',
            default='draft',
            choices=('draft', 'publish', 'private'),
            help='the post status, defaults to %(default)s',
        )
        parser.add_argument(
            'filename',
            help='the file containing the post body',
        )
        return parser

    def _take_action(self, parsed_args):
        with open(parsed_args.filename, 'r',
                  encoding=parsed_args.encoding) as f:
            raw_body = f.read()
        formatted_body = markdown.markdown(raw_body)

        if parsed_args.dry_run:
            print('New %s post "%s":\n' %
                  (parsed_args.status, parsed_args.title))
            print(formatted_body)
        else:
            post = WordPressPost()
            post.title = parsed_args.title
            post.content = formatted_body
            post.post_status = parsed_args.status
            self.wp.call(NewPost(post))
