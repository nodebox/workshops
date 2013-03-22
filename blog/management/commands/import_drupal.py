from optparse import make_option
import time
import os
import shutil
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import MySQLdb

from blog.models import Blog, Entry, Asset


class Command(BaseCommand):
    help = 'Import blog entries from Drupal'
    option_list = BaseCommand.option_list + (
        make_option('-d',
                    dest='database',
                    help='The Drupal database name'),
        make_option('-u',
                    dest='user',
                    help='The Drupal database user'),
        make_option('-p',
                    dest='password',
                    help='The Drupal database password'),
        make_option('-r',
                    dest='root',
                    help='The Drupal root directory (for copying image files)'),
        make_option('-b',
                    dest='blog_id',
                    help='The Django destionation blog id. Should exist.'))

    def handle(self, *args, **options):
        blog = Blog.objects.get(id=options['blog_id'])
        blog.ensure_assets_directory()
        drupal_db = MySQLdb.Connect(db=options['database'], user=options['user'], passwd=options['password'])

        node_cursor = drupal_db.cursor()
        node_cursor.execute('select n.nid, u.name, u.mail, n.title, n.created, r.body from node as n, users as u, node_revisions as r where n.uid=u.uid and r.nid=n.nid')
        for row in list(node_cursor):
            row = dict(zip(['id', 'name', 'email', 'title', 'created', 'body'], row))

            print "create user %s" % row['name']
            # Ensure the user exists.
            try:
                user = User.objects.get(username=row['name'])
            except User.DoesNotExist:
                user = User.objects.create_user(row['name'], row['email'])

            # Create the blog entry.
            self.stdout.write('Create "%s"' % row['title'])

            entry = Entry.objects.create(blog=blog,
                                         user=user,
                                         title=row['title'],
                                         slug=str(row['id']),
                                         pub_date=datetime.fromtimestamp(row['created']),
                                         body=row['body'])

            # Create the files.
            file_cursor = drupal_db.cursor()
            file_cursor.execute("select f.filepath from files as f where f.filename='_original' and f.nid=%s" % row['id'])
            image_files = [ir[0] for ir in file_cursor]
            for i, f in enumerate(image_files):
                position = i + 1
                print f, position
                src_file = os.path.join(options['root'], f)
                dst_file = os.path.join(blog.assets_directory, os.path.basename(f))
                if os.path.exists(src_file):
                    print src_file, "->", dst_file
                    shutil.copyfile(src_file, dst_file)
                    Asset.objects.create(entry=entry,
                                         file_name=os.path.basename(dst_file),
                                         type='image',
                                         description='',
                                         position=position)
