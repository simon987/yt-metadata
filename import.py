import json
import os
import psycopg2

DB_STR = "dbname=yt-meta user=yt-meta"
tags_cache = {}
categories_cache = {}
licenses_cache = {}


def init_cache():

    with psycopg2.connect(DB_STR) as conn:

        cursor = conn.cursor()

        # Tags
        cursor.execute('SELECT id, name FROM tag')
        for tag in cursor.fetchall():
            tags_cache[tag[1]] = tag[0]

        # Categories
        cursor.execute('SELECT id, name FROM category')
        for category in cursor.fetchall():
            categories_cache[category[1]] = category[0]

        # License
        cursor.execute('SELECT id, name FROM license')
        for license in cursor.fetchall():
            licenses_cache[license[1]] = license[0]


def create_tag(cursor, tag, video_id):
    tag_id = tags_cache.get(tag, None)
    if not tag_id:
        cursor.execute('INSERT INTO tag (name) VALUES (%s)', (tag, ))
        cursor.execute('SELECT LASTVAL()')

        tag_id = cursor.fetchone()[0]
        tags_cache[tag] = tag_id
        print("Created tag '" + tag + "' with id " + str(tag_id))
    cursor.execute('INSERT INTO video_has_tag (video_id, tag_id) VALUES (%s,%s)', (video_id, tag_id))


def create_category(cursor, category, video_id):

    category_id = categories_cache.get(category, None)
    if not category_id:
        cursor.execute('INSERT INTO category (name) VALUES (%s)', (category, ))
        cursor.execute('SELECT LASTVAL()')

        category_id = cursor.fetchone()[0]
        categories_cache[category] = category_id
        print("Created category '" + category + "' with id " + str(category_id))
    cursor.execute('INSERT INTO video_in_category (video_id, category_id) VALUES (%s,%s)', (video_id, category_id))


def create_uploader(cursor, name, ul_id, url):

    cursor.execute('INSERT INTO uploader (id, url, name) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING',
                   (ul_id, url, name))


def create_license(cursor, name):

    license_id = licenses_cache.get(name, None)
    if not license_id:
        cursor.execute('INSERT INTO license (name) VALUES (%s)', (name, ))
        cursor.execute('SELECT LASTVAL()')

        license_id = cursor.fetchone()[0]
        licenses_cache[name] = license_id
        print("Created license '" + name + "' with id " + str(license_id))


def create_video(cursor, **kwargs):

    cursor.execute('INSERT INTO video (id, uploader_id, creator, upload_date, license_id, title, full_title,'
                   ' alt_title, file_name, description, annotation, webpage_url, view_count, like_count, '
                   'dislike_count, display_id, duration, age_limit) '
                   'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '
                   'ON CONFLICT DO NOTHING ',
                   (kwargs["id"],
                    kwargs["uploader_id"], kwargs["creator"], kwargs["upload_date"],
                    kwargs["license_id"],
                    kwargs["title"], kwargs["full_title"], kwargs["alt_title"],
                    kwargs["file_name"],
                    kwargs["description"],
                    kwargs["annotation"],
                    kwargs["webpage_url"],
                    kwargs["view_count"], kwargs["like_count"], kwargs["dislike_count"],
                    kwargs["display_id"],
                    kwargs["duration"],
                    kwargs["age_limit"]
                    ))

    print("Created video " + kwargs["id"])


def create_subtitles(cursor, filename, lang, url, video_id):

    with open(filename, "r") as f:
        data = f.read()

        cursor.execute('INSERT INTO subtitles (language, url, data, video_id) VALUES (%s,%s,%s,%s) '
                       'ON CONFLICT DO NOTHING',
                       (lang, url, data, video_id))
        print("Create subtitles " + lang + " for " + video_id)


def create_thumbnail(cursor, filename, url, tn_id, video_id):

    if filename and os.path.exists(filename):
        with open(filename, "rb") as f:
            data = psycopg2.Binary(f.read())
    else:
        data = None

    cursor.execute('INSERT INTO thumbnail (thumbnail_id, url, video_id, data) VALUES (%s,%s,%s,%s) '
                   'ON CONFLICT DO NOTHING',
                   (tn_id, url, video_id, data))
    print("Create thumbnail " + tn_id + " for " + video_id)


def create_format(cursor, **kwargs):
    cursor.execute('INSERT INTO format (name, note, format_id, url, player_url, extension, audio_codec, video_codec, '
                   'audio_bitrate, total_bitrate, file_size, quality, width, height, fps, video_id) '
                   'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '
                   'ON CONFLICT DO NOTHING ',
                   (kwargs["name"],
                    kwargs["note"],
                    kwargs["format_id"],
                    kwargs["url"],
                    kwargs["player_url"],
                    kwargs["extension"],
                    kwargs["audio_codec"],
                    kwargs["video_codec"],
                    kwargs["audio_bitrate"],
                    kwargs["total_bitrate"],
                    kwargs["file_size"],
                    kwargs["quality"],
                    kwargs["width"], kwargs["height"],
                    kwargs["fps"],
                    kwargs["video_id"]
                    ))
    print("Create format " + kwargs["format_id"] + " for " + kwargs["video_id"])


def create_chapter(cursor, video_id, start_time, end_time, title):

    cursor.execute('INSERT INTO chatper (start_time, end_time, title, video_id) VALUES (%s,%s,%s,%s) '
                   'ON CONFLICT DO NOTHING',
                   (start_time, end_time, title, video_id))
    print("Created chapter for " + video_id)


def import_json(filename):

    directory = filename[:filename.rfind("/") + 1]

    with open(filename, "r") as f:

        meta = json.load(f)

        with psycopg2.connect(DB_STR) as conn:

            cursor = conn.cursor()

            create_license(cursor, meta["license"])

            create_uploader(cursor, meta["uploader"], meta["uploader_id"], meta["uploader_url"])

            create_video(cursor,
                         id=meta["id"],
                         uploader_id=meta["uploader_id"],
                         creator=meta["creator"],
                         upload_date=meta["upload_date"],
                         license_id=licenses_cache[meta["license"]],
                         title=meta["title"],
                         full_title=meta["fulltitle"],
                         alt_title=meta["alt_title"],
                         file_name=meta["_filename"],
                         description=meta["description"],
                         duration=meta["duration"],
                         age_limit=meta["age_limit"],
                         annotation=meta["annotations"],
                         webpage_url=meta["webpage_url"],
                         view_count=meta["view_count"],
                         like_count=meta["like_count"],
                         dislike_count=meta["dislike_count"],
                         display_id=meta["display_id"])

            for tag in meta["tags"]:
                create_tag(cursor, tag, meta["id"])

            for category in meta["categories"]:
                create_category(cursor, category, meta["id"])

            for sub in meta["subtitles"]:
                sub_filename = directory + meta["_filename"].replace(meta["ext"], sub + ".vtt")
                if os.path.exists(filename):
                    create_subtitles(cursor, sub_filename, sub, meta["subtitles"][sub][0]["url"], meta["id"])

            for tn in meta["thumbnails"]:
                # With the script, only the first (default) thumbnail is saved
                if tn["id"] == "0":
                    tn_filename = directory + meta["_filename"].replace(meta["ext"], "jpg")
                else:
                    tn_filename = None

                create_thumbnail(cursor, tn_filename, tn["url"], tn["id"], meta["id"])

            for frmt in meta["formats"]:
                create_format(cursor,
                              name=frmt["format"],
                              note=frmt.get("format_note", None),
                              format_id=frmt["format_id"],
                              url=frmt["url"],
                              player_url=frmt.get("player_url", None),
                              extension=frmt["ext"],
                              audio_codec=frmt["acodec"],
                              video_codec=frmt["vcodec"],
                              audio_bitrate=frmt.get("abr", None),
                              total_bitrate=frmt.get("tbr", None),
                              file_size=frmt.get("filesize", None),
                              quality=frmt.get("quality", None),
                              width=frmt.get("width", None),
                              height=frmt.get("height", None),
                              fps=frmt.get("fps", None),
                              video_id=meta["id"])

            if meta["chapters"]:
                for chapter in meta["chapters"]:
                    create_chapter(cursor, meta["id"], chapter["start_time"], chapter["end_time"], chapter["title"])

            if meta["automatic_captions"]:
                print(meta["id"])
                quit()


def import_recursive(root_path):

    for root, dirs, files in os.walk(root_path):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext == ".json":
                filename = os.path.join(root, file)
                import_json(filename)


init_cache()
import_recursive("/home/simon/Downloads/yt/")
