from optparse import make_option
import os
import shutil

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import MySQLdb

from blog.models import Blog, Post, Asset


class Command(BaseCommand):
    help = 'Import blog posts from Movable Type'
    option_list = BaseCommand.option_list + (
        make_option('-d',
                    dest='database',
                    help='The MT database name'),
        make_option('-u',
                    dest='user',
                    help='The MT database user'),
        make_option('-p',
                    dest='password',
                    help='The MT database password'),
        make_option('-r',
                    dest='root',
                    help='The MT root directory (for copying image files)'),
        make_option('-i',
                    dest='src_blog_id',
                    help='The MT blog ID to copy'),
        make_option('-b',
                    dest='dst_blog_id',
                    help='The Django destionation blog id. Should exist.'))

    def handle(self, *args, **options):
        blog = Blog.objects.get(id=options['dst_blog_id'])
        blog.ensure_assets_directory()
        db = MySQLdb.Connect(db=options['database'], user=options['user'], passwd=options['password'])
        entry_cursor = db.cursor()
        entry_cursor.execute('''
            select e.entry_id, e.entry_basename, e.entry_modified_on, e.entry_title, e.entry_text,
                   a.author_basename, a.author_email, a.author_nickname
                   from mt_entry as e, mt_author as a
                   where e.entry_blog_id = %s
                     and e.entry_author_id = a.author_id''' % options['src_blog_id'])
        print list(entry_cursor)

        for row in list(entry_cursor):
            row = dict(zip(['id', 'basename', 'modified_on', 'title', 'body', 'username', 'email', 'first_name'], row))

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
                post = Post.objects.get(blog=blog, user=user, slug=row['basename'])
            except Post.DoesNotExist:
                post = Post.objects.create(blog=blog,
                                           user=user,
                                           title=row['title'] or '<No Title>',
                                           slug=row['basename'][:50],
                                           pub_date=row['modified_on'],
                                           body=row['body'])

            # Create the files.
            asset_cursor = db.cursor()
            asset_cursor.execute('''select a.asset_file_path, a.asset_class
                                    from mt_asset as a, mt_objectasset as oa
                                    where oa.objectasset_object_id = %s
                                      and oa.objectasset_blog_id = %s
                                      and a.asset_id = oa.objectasset_asset_id''' % (row['id'], options['src_blog_id']))

            for i, asset in enumerate(list(asset_cursor)):
                position = i + 1
                asset = dict(zip(['file_path', 'asset_class'], asset))
                src_file = asset['file_path'].replace(r'%r', options['root'])
                print src_file
                dst_file = os.path.join(blog.assets_directory, os.path.basename(asset['file_path']))

                if os.path.exists(src_file):
                    print src_file, "->", dst_file
                    shutil.copyfile(src_file, dst_file)
                    Asset.objects.create(post=post,
                                         file_name=os.path.basename(dst_file),
                                         type=asset['asset_class'],
                                         description='',
                                         position=position)
