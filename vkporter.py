#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    :mod:`vkporter`
    ~~~~~~~~~~~~~~~

    A micro tool for export photo albums from `vk.com <https://vk.com>`_.

     Download all albums withouth: My profile photos, My wall photos, Saved photos.

     It's based on `VK_API <https://github.com/python273/vk_api>`_
     by Kirill Python <mikeking568@gmail.com>,
     `Requests <python-requests.org>`_
     and `ProgressBar <https://code.google.com/p/python-progressbar/>`_.

    :copyright: (c) 2013 by Andrey Maksimov.
    :license: BSD, see LICENSE for more details.
"""
__author__ = 'Andrey Maksimov <meamka@me.com>, Mr. Vice-Versa'
__date__ = '15.06.2015'
__version__ = '0.2.1'


import argparse
import datetime
from getpass import getpass
import os
import time
import sys
import templates
import traceback

# According to API doc, they return maximum 100 in getComments and getWall
# We request 100 and assume that if less is returned then there's no more left
items_per_request = 100

try:
    import requests
except ImportError:
    print("Cannot find 'requests' module. Please install it and try again.")
    sys.exit(0)

try:
    from vk_api import VkApi, AuthorizationError
except ImportError:
    print("Cannot find 'vk_api' module. Please install it and try again.")
    sys.exit(0)


def find_key(fdict, key):
    """Find key in dict.
    """
    for k, v in fdict.items():
        if key in fdict:
            return fdict[key]
        if isinstance(k, dict):
            return find_key(k, key)
        elif isinstance(v, dict):
            return find_key(v, key)
        else:
            return None


def get_user_id(connection, step=0, max_step=2):
    user_id = find_key(connection.settings.all, 'user_id')

    # Call VkApi.authorization() by hand, to get user_id from VkApi.settings.
    # VkApi has the bug.
    if step >= max_step:
        return user_id
    if user_id:
        return user_id
    else:
        try:
            connection.authorization()
            # You can call also
            # connection.vk_login()
            # connection.api_login()
        except:
            print step, user_id, connection.settings.all
        step = step + 1
        return get_user_id(connection, step=step)

def connect(login, password, owner_id=None):
    """Initialize connection with `vk.com <https://vk.com>`_ and try to authorize user with given credentials.

    :param login: user login e. g. email, phone number
    :type login: str
    :param password: user password
    :type password: str

    :return: :mod:`vk_api.vk_api.VkApi` connection
    :rtype: :mod:`VkApi`
    """
    connection = VkApi(login, password)
    connection.authorization()
    connection.owner_id = owner_id or get_user_id(connection)
    return connection


def get_albums(connection):
    """Get albums list for currently authorized user.

    :param connection: :class:`vk_api.vk_api.VkApi` connection
    :type connection: :class:`vk_api.vk_api.VkApi`

    :return: list of photo albums or ``None``
    :rtype: list
    """
    try:
        return connection.method(
            'photos.getAlbums',
                {'owner_id': connection.owner_id}
        )
    except Exception as e:
        print(e)
        return None


def gen_header(album, output):
    gen_page = open(os.path.join(output, 'generated.html'), 'w')
    gen_page.write(templates.header.substitute(title=album['title']).encode('utf8'))
    return gen_page


def gen_footer(gen_page):
    gen_page.write(templates.footer)
    gen_page.close()


def write_author(gen_page, profiles, item):
    from_id = item['from_id']
    author = next(x for x in profiles if x['id'] == from_id)
    formatted_date = datetime.datetime.fromtimestamp(item['date']).strftime(templates.date_format_posts)

    gen_page.write(templates.author_line.substitute(
            author_name=author['first_name'],
            author_family=author['last_name'],
            date=formatted_date).encode('utf8'))


def write_comments(gen_page, items, profiles):
    if items and len(items) > 0:
        gen_page.write(templates.comments_begin.substitute(num=len(items)).encode('utf8'))
        for comment in items:
            write_author(gen_page, profiles, comment)
            gen_page.write(templates.comment_text.substitute(
                    text=comment['text']).encode('utf8'))
        gen_page.write(templates.comments_end)


def write_gen(gen_page, connection, photo, title):
    gen_page.write((templates.photoline.substitute(title=title, text=photo['text'])).encode('utf8'))
    comments, profiles = get_comments(connection, photo['id'], False)
    write_comments(gen_page, comments, profiles)


def download_album(connection, output_path, date_format, album, prev_s_len=0):
    if album['id'] == 'user':
        response = get_user_photos(connection)
    else:
        response = get_photos(connection, album['id'])

    output = os.path.join(output_path, album['title'])
    if not os.path.exists(output):
        os.makedirs(output)

    gen_page = gen_header(album, output)

    photos_count = response['count']
    photos = response['items']
    processed = 0

    for photo in photos:
        percent = round(float(processed) / float(photos_count) * 100, 2)
        output_s = "\rExporting %s... %s of %s (%2d%%)" % (album['title'], processed, photos_count, percent)
        # Pad with spaces to clear the previous line's tail.
        # It's ok to multiply by negative here.
        output_s += ' '*(prev_s_len - len(output_s))
        sys.stdout.write(output_s)
        prev_s_len = len(output_s)
        sys.stdout.flush()

        title = download_photo(connection, photo, output, date_format)
        write_gen(gen_page, connection, photo, title)
        processed += 1

        # crazy hack to prevent vk.com "Max retries exceeded" error
        # pausing download process every 50 photos
        if processed % 50 == 0:
            time.sleep(1)
    gen_footer(gen_page)


def get_user_photos(connection):
    """Get user photos list"""
    try:
        return connection.method(
            'photos.getUserPhotos',
                {'count': 1000,
                'owner_id': connection.owner_id}
        )
    except Exception as e:
        print(e)
        return None


def get_photos(connection, album_id):
    """Get photos list for selected album.

    :param connection: :class:`vk_api.vk_api.VkApi` connection
    :type connection: :class:`vk_api.vk_api.VkApi`
    :param album_id: album identifier returned by :func:`get_albums`
    :type album_id: int

    :return: list of photo albums or ``None``
    :rtype: list
    """
    try:
        return connection.method(
            'photos.get',
                {'album_id': album_id,
                'owner_id': connection.owner_id}
        )
    except Exception as e:
        print(e)
        return None


def get_comments(connection, item_id, is_wall):
    """Get comments list for specified photo.

    :param connection: :class:`vk_api.vk_api.VkApi` connection
    :type connection: :class:`vk_api.vk_api.VkApi`
    :param item_id: album identifier returned by :func:`get_photos` or 'get_wall'
    :param is_wall: True for getting comments of wall post, false for comments for photo
    :type item_id: int

    :return: list of comments or ``None``
    :rtype: list
    """
    try:
        items = []
        profiles = []
        while True:
            temp = connection.method(
                    'wall.getComments' if is_wall else 'photos.getComments',
                    {('post_id' if is_wall else 'photo_id'): item_id,
                     'owner_id': connection.owner_id,
                     'extended': 1,
                     'offset': len(items),
                     'count': items_per_request
                     }
            )
            items += temp['items']
            profiles += temp['profiles']
            if len(temp['items']) != items_per_request:
                break
        return items, profiles
    except Exception as e:
        print(e)
        return None, None


def get_wall(connection):
    try:
        items = []
        profiles = []
        while True:
            temp = connection.method(
                'wall.get',
                    {'owner_id': connection.owner_id,
                     'extended': 1,
                     'offset': len(items),
                     'count': items_per_request
                     }
            )
            if len(temp['items']) == 0:
                break
            items += temp['items']
            profiles += temp['profiles']

        return items, profiles
    except Exception as e:
        print(e)
        return None, None



def download_photo(connection, photo, output, date_format):
    """Download photo

    :param photo:
    """
    #url = photo.get('photo_2560') or photo.get('photo_1280') or photo.get('photo_807') or photo.get('photo_604') or photo.get('photo_130')
    url = photo.get('photo_807') or photo.get('photo_604') or photo.get('photo_130') or photo.get('photo_2560') or photo.get('photo_1280') or photo.get('photo_807') or photo.get('photo_604') or photo.get('photo_130')

    formatted_date = datetime.datetime.fromtimestamp(photo['date']).strftime(date_format)
    title = '%s_%s' % (formatted_date, photo['id'])
    path = os.path.join(output, '%s.jpg' % title)
    need_download = not os.path.isfile(path)
    if need_download:
        r = requests.get(url)
        with open(path, 'wb') as f:
            for buf in r.iter_content(1024):
                if buf:
                    f.write(buf)
    return title


def sizeof_fmt(num):
    """Small function to format numbered size to human readable string

    :param num: bytes to format
    :type num: int

    :return: human readable size
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def save_wall(connection, output_path, date_format):
    items, profiles = get_wall(connection)
    output = os.path.join(output_path, 'wall')
    if not os.path.exists(output):
        os.makedirs(output)
    gen_page = open(os.path.join(output, 'generated.html'), 'w')
    gen_page.write(templates.header.substitute(title=u'Стена').encode('utf8'))
    processed = 0
    total = len(items)
    prev_s_len = 0

    for item in items:
        percent = round(float(processed) / float(total) * 100, 2)
        output_s = "\rExporting wall... %s of %s items (%2d%%)" % (processed, total, percent)
        # Pad with spaces to clear the previous line's tail.
        # It's ok to multiply by negative here.
        output_s += ' '*(prev_s_len - len(output_s))
        sys.stdout.write(output_s)
        prev_s_len = len(output_s)
        sys.stdout.flush()
        processed += 1

        write_author(gen_page, profiles, item)
        gen_page.write(templates.comment_text.substitute(
                text=item['text']).encode('utf8'))
        attachments = item.get('attachments')
        if attachments and len(attachments) > 0:
            gen_page.write(templates.wall_photo_begin)
            count = 0
            for attach in attachments:
                count += 1
                if count % 5 == 0:
                    gen_page.write(templates.wall_photo_newline)
                if attach['type'] == 'photo':
                    title = download_photo(connection, attach['photo'], output, date_format)
                    gen_page.write(templates.wall_photo_content.substitute(
                            title=title).encode('utf8'))
            gen_page.write(templates.wall_photo_end)
        comments, comment_profiles = get_comments(connection, item['id'], True)
        write_comments(gen_page, comments, comment_profiles)

    gen_page.write(templates.footer)
    gen_page.close()

if __name__ == '__main__':

    # Connect to vk.com
    # Get list of user albums
    # For every album do the follow:
    # # create folder if not exists
    # # get list of photos
    # # download photo and put it in album folder
    # # do it while have photos
    # do it while have albums

    parser = argparse.ArgumentParser(description='', version='%(prog)s ' + __version__)
    parser.add_argument('username', help='vk.com username')
    parser.add_argument('-o', '--output', help='output path to store photos',
                        default=os.path.abspath(os.path.join(os.path.dirname(__file__), 'exported')))
    parser.add_argument('-f', '--date_format', help='for photo title', default='%Y%m%d@%H%M')
    parser.add_argument('-a', '--album_id', help='dowload a particular album. Additional values: wall, profile, saved, user')
    parser.add_argument('-id', '--owner_id', help='User ID')
    parser.add_argument('-w', '--wall', action='store_true', help='Save wall contents (only)')
    parser.add_argument('-b', '--backup', action='store_true', help='Make full backup (save photos, wall, generate html)')

    args = parser.parse_args()

    # expand user path if necessary
    if args.output.startswith('~'):
        args.output = os.path.expanduser(args.output)

    start_time = datetime.datetime.now()
    try:
        password = getpass("Password: ")
        if not password:
            print('Password too short')
            sys.exit(0)

        # Initialize vk.com connection
        try:
            connection = connect(args.username, password, owner_id=args.owner_id)
        except AuthorizationError as error_msg:
            print(error_msg)
            sys.exit()

        if args.wall or args.backup:
            save_wall(connection, args.output, args.date_format)

        if not args.wall or args.backup:
            # Request list of photo albums
            albums_response = get_albums(connection)
            albums_count = albums_response['count']
            albums = albums_response['items']

        if args.album_id:
            # dowload a particular album
            #find album title
            album = None
            for i in albums:
                if i['id'] == int(args.album_id):
                    album = i
                    break
            if album is None:
                print 'Album with id ', args.album_id, ' not found'
                sys.exit(1)

            download_album(connection, args.output, args.date_format, album)
        # download all albums
        elif args.backup:
            all_photos_count = 0

            print '\n'
            print("Found %s album%s:" % (albums_count, 's' if albums_count > 1 else ''))

            ix = 0
            for album in albums:
                print('%3d. %-40s %4s item%s' % (
                    ix + 1, album['title'], album['size'], 's' if int(album['size']) > 1 else ''))
                ix += 1
                all_photos_count += album['size']
            print ' == All photos {0} == \n'.format(all_photos_count)

            # Sleep to prevent max request count
            time.sleep(1)

            if not os.path.exists(args.output):
                os.makedirs(args.output)

            for album in albums:
                download_album(connection, args.output, args.date_format, album)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e)
        traceback.print_exc()
        print(exc_type, fname, exc_tb.tb_lineno)

        sys.exit(1)

    except KeyboardInterrupt:
        print('VKPorter exporting stopped by keyboard')
        sys.exit(0)

    finally:
        print '\n'
        print("Done in %s" % (datetime.datetime.now() - start_time))
