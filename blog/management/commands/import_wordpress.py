from optparse import make_option
import os
import shutil

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import MySQLdb

from blog.models import Blog, Post, Asset

MIME_MAPPINGS = {
    'image/png': 'image',
    'image/jpeg': 'image',
    'image/gif': 'image',
    'video/quicktime': 'movie',
    'application/zip': 'zip',
    'application/pdf': 'pdf',
    'application/octet-stream': 'source'
}


class Command(BaseCommand):
    help = 'Import blog posts from Wordpress'
    option_list = BaseCommand.option_list + (
        make_option('-d',
                    dest='database',
                    help='The WP database name'),
        make_option('-u',
                    dest='user',
                    help='The WP database user'),
        make_option('-p',
                    dest='password',
                    help='The WP database password'),
        make_option('-r',
                    dest='root',
                    help='The WP root directory (for copying image files)'),
        make_option('-b',
                    dest='blog_id',
                    help='The Django destination blog id. Should exist.'))

    def handle(self, *args, **options):
        assert options['root'].endswith('/wp-content/uploads/')
        blog = Blog.objects.get(id=options['blog_id'])
        blog.ensure_assets_directory()
        db = MySQLdb.Connect(db=options['database'], user=options['user'], passwd=options['password'])
        posts_cursor = db.cursor()
        posts_cursor.execute('''
            select p.id, p.post_name, p.post_date, p.post_title, p.post_content,
                   u.user_login, u.display_name, u.user_email
                   from wp_posts as p, wp_users as u
                   where p.post_type = 'post'
                     and p.post_status = 'publish'
                     and p.post_author = u.id''')

        for row in list(posts_cursor):
            row = dict(zip(['id', 'post_name', 'post_date', 'title', 'body', 'username', 'first_name', 'email'], row))

            print "create user %s" % row['username']
            # Ensure the user exists.
            try:
                user = User.objects.get(username=row['username'])
            except User.DoesNotExist:
                user = User.objects.create_user(row['username'], row['email'])
                user.first_name = row['first_name']
                user.save()

            # Create the blog post.
            self.stdout.write('Create "%s"' % row['title'])

            try:
                post = Post.objects.get(blog=blog, user=user, slug=row['post_name'])
            except Post.DoesNotExist:
                post = Post.objects.create(blog=blog,
                                           user=user,
                                           title=row['title'] or '<No Title>',
                                           slug=row['post_name'][:50],
                                           pub_date=row['post_date'],
                                           body=row['body'])

            # Create the files.
            asset_cursor = db.cursor()
            asset_cursor.execute('''select p.guid, p.post_mime_type
                                    from wp_posts as p
                                    where p.post_parent = %s
                                      and p.post_type = 'attachment' ''' % row['id'])

            for i, asset in enumerate(list(asset_cursor)):
                position = i + 1
                asset = dict(zip(['url', 'mime_type'], asset))
                src_file = os.path.join(options['root'], os.path.basename(asset['url']))
                print src_file
                dst_file = os.path.join(blog.assets_directory, os.path.basename(asset['url']))

                if os.path.exists(src_file):
                    print src_file, "->", dst_file
                    shutil.copyfile(src_file, dst_file)
                    Asset.objects.create(post=post,
                                         file_name=os.path.basename(dst_file),
                                         type=MIME_MAPPINGS.get(asset['mime_type'], 'file'),
                                         description='',
                                         position=position)
