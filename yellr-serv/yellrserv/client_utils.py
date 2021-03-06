import json
import datetime
import os
import uuid

import markdown

import subprocess
import magic
import mutagen.mp3
import mutagen.oggvorbis
import mutagen.mp4

import utils
from config import system_config

from pyramid.response import Response

from .models import (
    DBSession,
    #UserTypes,
    #Users,
    #Clients,
    Assignments,
    #Questions,
    #QuestionAssignments,
    #Languages,
    Posts,
    Votes,
    #MediaTypes,
    MediaObjects,
    #PostMediaObjects,
    Stories,
    ClientLogs,
    #Collections,
    #CollectionPosts,
    Messages,
    Notifications,
    Clients,
    )

def log_client_action(client, url, lat, lng, request, result, success):

    client_log = None

    try:

        client_id = None
        if client != None:
            client_id = client.client_id

        # no longer loging this, based on ... not a good idea.

        '''
        client_log = ClientLogs.log(
            session = DBSession,
            client_id = client_id,
            url = url,
            lat = lat,
            lng = lng,
            request = json.dumps({
                'get': '{0}'.format(request.GET),
                'post': '{0}'.format(request.POST),
            }),
            result = json.dumps(result),
            success = success,
        )
        '''

    except:
        raise Exception("Database error.")

    return client_log

def register_client(request):

    success = False
    error_text = ''
    language_code = ''
    lat = 0
    lng = 0
    client = None
    try:
        cuid = request.GET['cuid']
        language_code = request.GET['language_code']
        lat = float(request.GET['lat'])
        lng = float(request.GET['lng'])

        #print request.GET
        #print request.POST

        print '{0}: {1}'.format(cuid, request.url)

        # creates client if not yet seen
        client = Clients.get_client_by_cuid(
            session = DBSession,
            cuid = cuid,
            lat = lat,
            lng = lng,
        )

        Clients.check_in(
            session = DBSession,
            cuid = cuid,
            lat = lat,
            lng = lng,
        )

        success = True
    except:
        error_text = "Required Fields: cuid, language_code, lat, lng"

    return success, error_text, language_code, lat, lng, client

def get_assignments(client_id, language_code, lat, lng):

    ret_assignments = []
    
    try:

        assignments = Assignments.get_all_open_with_questions(
            session = DBSession,
            language_code = language_code,
            lat = lat,
            lng = lng,
            client_id = client_id,
        )
        
        for assignment_id, publish_datetime, expire_datetime, name, \
                    top_left_lat, top_left_lng, bottom_right_lat, \
                    bottom_right_lng, use_fence, collection_id, org_id, \
                    org_name, org_description, question_text, \
                    question_type_id, description, answer0, \
                    answer1, answer2, answer3, answer4, answer5, answer6, \
                    answer7, answer8, answer9, language_id, language_code, \
                    post_count, has_responded in assignments:
            ret_assignments.append({
                    'assignment_id': assignment_id,
                    #'organization_id': org_id,
                    'organization': org_name,
                    'organization_description': org_description,
                    'publish_datetime': str(publish_datetime),
                    'expire_datetime': str(expire_datetime),
                    'name': name,
                    'top_left_lat': top_left_lat,
                    'top_left_lng': top_left_lng,
                    'bottom_right_lat': bottom_right_lat,
                    'bottom_right_lng': bottom_right_lng,
                    'question_text': question_text,
                    'question_type_id': question_type_id,
                    'description': description,
                    'answer0': answer0,
                    'answer1': answer1,
                    'answer2': answer2,
                    'answer3': answer3,
                    'answer4': answer4,
                    'answer5': answer5,
                    'answer6': answer6,
                    'answer7': answer7,
                    'answer8': answer8,
                    'answer9': answer9,
                    'language_code': language_code,
                    'post_count': post_count,
                    'has_responded': has_responded,
                })

    except:
        raise Exception("Database error.")

    return ret_assignments

def get_stories(language_code, lat, lng, start, count):

    ret_stories = []

    try:

        stories, total_story_count = Stories.get_stories(
            session = DBSession,
            lat = lat,
            lng = lng,
            language_code = language_code,
            start = start,
            count = count,
        )

        for story_unique_id, publish_datetime, edited_datetime, title, tags, \
                    contents, top_left_lat, top_left_lng, bottom_right_lat, \
                    bottom_right_lng, first_name, last_name, organization_id, \
                    organization_name, email in stories:
            ret_stories.append({
                'story_unique_id': story_unique_id,
                'publish_datetime': str(publish_datetime),
                'publish_datetime_ago': utils.ago_decode(publish_datetime),
                'edited_datetime': str(edited_datetime),
                'title': title,
                'tags': tags,
                #'top_text': top_text,
                #'contents': contents,
                'contents_rendered': markdown.markdown(contents),
                'top_left_lat': top_left_lat,
                'top_left_lng': top_left_lng,
                'bottom_right_lat': bottom_right_lat,
                'bottom_right_lng': bottom_right_lng,
                'author_first_name': first_name,
                'author_last_name': last_name,
                'author_organization': organization_name,
                'author_email': email,
                #'banner_media_file_name': media_file_name,
                #'banner_media_id': media_id,
            })

    except:
        raise Exception("Database error.")

    return ret_stories

def get_notifications(client_id, language_code, lat, lng):

    ret_notifications = []

    try:

        notifications = Notifications.get_notifications_from_client_id(
            session = DBSession,
            client_id = client_id, #client.client_id,
        )

        for notification_id, notification_datetime, \
                notification_type, payload in notifications:
            ret_notifications.append({
                'notification_id': notification_id,
                'notification_datetime': str(notification_datetime),
                'notification_type': notification_type,
                'payload': json.loads(payload),
            })

    except:
        raise Exception("Database error.")

    return ret_notifications

def get_messages(client_id, language_code, lat, lng):

    ret_messages = []
    
    try:

        messages = Messages.get_messages_from_client_id(
            session = DBSession,
            client_id = client_id, #client.client_id
        )
        
        for message_id, from_user_id,to_user_id,message_datetime, \
                parent_message_id,subject,text, was_read,from_organization, \
                from_first_name,from_last_name in messages:
            ret_messages.append({
                'message_id': message_id,
                'from_user_id': from_user_id,
                'to_user_id': to_user_id,
                'from_organization': from_organization,
                'from_first_name': from_first_name,
                'from_last_name': from_last_name,
                'message_datetime': str(message_datetime),
                'parent_message_id': parent_message_id,
                'subject': subject,
                'text': text,
                'was_read': was_read,
            })
            
    except:
        raise Exception("Database error.")

    return ret_messages

def create_response_message(client_id, parent_message_id, subject, text):

    message = None

    try:

        message = Messages.create_response_message_from_http(
            session = DBSession,
            client_id = client_id,
            parent_message_id = parent_message_id,
            subject = subject,
            text = text,
        )
        
    except:
        raise Exception("Database error.")

    return message

def get_approved_posts(client_id, language_code, lat, lng, start, count):
    
    ret_posts = []
    
    try:

        posts = Posts.get_all_approved_from_location(
            session = DBSession,
            client_id = client_id,
            language_code = language_code,
            lat = lat,
            lng = lng,
            start = start,
            count = count,
        )
        
        ret_posts = utils._decode_posts(posts, clean=True)
        
    except:
        raise Exception("Database error.")

    return ret_posts 

def get_post(post_id):

    ret_post = None

    #try:
    if True:
        post = Posts.get_with_media_objects_from_post_id(
            session = DBSession,
            post_id = post_id,
        )

        print "\n\n"
        print post
        print "\n\n"

        if not post is None and len(post) != 0:
            ret_post = utils._decode_posts(post, clean=False)[0]

    #except:
    #    raise Exception("Database error.")

    return ret_post

def register_vote(post_id, client_id, is_up_vote):

    vote = None
    
    try:

        vote = Votes.register_vote(
            session = DBSession,
            post_id = post_id,
            client_id = client_id,
            is_up_vote = is_up_vote,
        )

    except:
        raise Exception("Database error.")

    return vote

def save_input_file(input_file):

    # generate a unique file name to store the file to
    unique = str(uuid.uuid4())
    filename = os.path.join(system_config['upload_dir'], unique)

    with open(filename, 'wb') as f:
        input_file.seek(0)
        while True:
            data = input_file.read(2<<16)
            if not data:
                break
            f.write(data)

    return filename

def process_image(base_filename):

    image_filename = ""
    preview_filename = ""

    try:

        image_filename = '{0}.jpg'.format(base_filename)
        preview_filename = '{0}p.jpg'.format(base_filename)

        # type incoming file
        mime_type = magic.from_file(base_filename, mime=True)
        allowed_image_types = [
            'image/jpeg',
            'image/png',
            'image/x-ms-bmp',
            'image/tiff',
        ]

        if not mime_type.lower() in allowed_image_types:
            raise Exception("Unsupported Image Type: %s" % mime_type)

        # convert to jpeg from whatever format it was
        try:
            subprocess.call(['convert', base_filename, image_filename])
        except Exception, ex:
            raise Exception("Error converting image: {0}".format(ex))

        #strip metadata from images with ImageMagick's mogrify
        try:
            subprocess.call(['mogrify', '-strip', image_filename])
        except Exception, ex:
            raise Exception("Error removing metadata: {0}".format(ex))

        # create preview image
        try:
            subprocess.call(['convert', image_filename, '-resize', '450', \
                '-size', '450', preview_filename])
        except Exception, ex:
            raise Exception("Error generating preview image: {0}".format(ex))

    except Exception, e:
        raise Exception(e)

    return image_filename, preview_filename

def process_video(base_filename):

    video_filename = ""
    preview_filename = ""

    #try:
    if True:
        '''
        # type incoming file
        mime_type = magic.from_file(base_filename, mime=True)
        allowed_image_types = [
            'video/mpeg',
            'video/mp4',
        ]

        if not mime_type.lower() in allowed_image_types:
            raise Exception("Unsupported Image Type: %s" % mime_type)

        #I can't seem to find any evidence of PII in mpg metadata
        if mime_type.lower() == 'video/mpeg':
            video_filename = '{0}.mpeg'.format(base_filename)
        elif mime_type.lower() == 'video/mp4':
            video_filename = '{0}.mp4'.format(base_filename)
            try:
                mp4 = mutagen.mp4.MP4(temp_file_path)
                mp4.delete()
                mp4.save()
            except:
                raise Exception("Something went wrong while stripping"
                                " metadata from mp4")

        #
        # TODO: create preview image for video
        #

        '''

        # type incoming file
        mime_type = magic.from_file(base_filename, mime=True)
        allowed_image_types = [
            'video/mpeg',
            'video/mp4',
            'video/quicktime',
            'video/3gpp',
        ]

        if not mime_type.lower() in allowed_image_types:
            raise Exception("Unsupported Image Type: %s" % mime_type)

        video_filename = '{0}.mp4'.format(base_filename)
        preview_filename = '{0}p.jpg'.format(base_filename)

        cmd = [
            'ffmpeg',
            '-i',
            base_filename,
            '-map_metadata',
            '-1',
            '-c:v',
            'copy',
            '-c:a',
            'copy',
            video_filename,
        ]
        resp = subprocess.call(cmd, stdout=subprocess.PIPE)

        print "\n\nCMD: {0}\n\n".format(' '.join(cmd))
        print "\n\nRESP: {0}\n\n".format(resp)

        if resp == 1:
            cmd = [
                'ffmpeg',
                '-i',
                base_filename,
                '-map_metadata',
                '-1',
                '-c:v',
                'copy',
                #'-c:a',
                #'copy',
                video_filename,
            ]
            resp = subprocess.call(cmd, stdout=subprocess.PIPE)

            print "\n\nCMD: {0}\n\n".format(' '.join(cmd))
            print "\n\nRESP: {0}\n\n".format(resp)
        
        cmd = [
            'ffmpeg',
            '-i',
            video_filename,
            '-ss',
            '00:00:01.00',
            '-vframes',
            '1',
            preview_filename,
        ]
        resp = subprocess.call(cmd, stdout=subprocess.PIPE)

        # create preview image
        #try:
        if True:
            subprocess.call(['convert', preview_filename, '-resize', '450', \
                '-size', '450', preview_filename], stdout=subprocess.PIPE)

            subprocess.call(['convert', preview_filename, './media/play-icon.png', \
                '-gravity', 'center', '-composite', preview_filename], stdout=subprocess.PIPE)
        #except Exception, ex:
        #    raise Exception("Error generating preview image: {0}".format(ex))

        #
        # TODO: create preview image for video
        #

       #raise Exception("Debug")

    #except Exception, e:
    #    raise Exception(e)

    return video_filename, preview_filename

def process_audio(base_filename):

    audio_filename = ""
    preview_filename = ""

    try:

        '''
        #mp3 file
        if mimetype == "audio/mpeg":
            audio_filename = '{0}.mp3'.format(base_filename)
            try:
                mp3 = mutagen.mp3.MP3(temp_file_path)
                mp3.delete()
                mp3.save()
            except:
                raise Exception("Something went wrong while stripping"
                                " metadata from mp3")
        #ogg vorbis file
        elif mimetype == "audio/ogg" or mimetype == "application/ogg":
            audio_filename = '{0}.ogg'.format(base_filename)
            try:
                ogg = mutagen.oggvorbis.Open(temp_file_path)
                ogg.delete()
                ogg.save()
            except:
                raise Exception("Something went wrong while stripping"
                                " metadata from ogg vorbis")

        #not mp3 or ogg vorbis
        else:
            raise Exception("invalid audio file")

        #
        # TODO: generic audio picture for preview name??
        #
        '''

        mime_type = magic.from_file(base_filename, mime=True)
        allowed_audio_types = [
            'audio/mpeg',
            'audio/ogg',
            'audio/x-wav',
            'audio/mp4',
            'video/3gpp',
        ]

        '''
        exts = [
            'mp3',
            'ogg',
            'wav',
            'mp4',
        ]
        '''

        if not mime_type.lower() in allowed_audio_types:
            raise Exception("Unsupported Audio Type: %s" % mime_type)

        audio_filename = '{0}.mp3'.format(base_filename)

        cmd = [
            'ffmpeg',
            '-i',
            base_filename,
            '-f',
            'mp3',
            '-map_metadata',
            '-1',
            #'-c:v',
            #'copy',
            #'-c:a',
            #'copy',
            audio_filename,
        ]
        resp = subprocess.call(cmd, stdout=subprocess.PIPE)

        print "\n\nCMD: {0}\n\n".format(' '.join(cmd))
        print "\n\nbase_filename: {0}\n\nRESP: {1}\n\n".format(base_filename, resp)

        #
        # TODO: generic audio picture for preview name??
        #

    except Exception, e:
        raise Exception(e)

    return audio_filename, preview_filename

def add_media_object(client_id, media_type_text, file_name, caption, \
        media_text):

    media_object = None
    try:

        media_object = MediaObjects.create_new_media_object(
            session = DBSession,
            client_id = client_id,
            media_type_text = media_type_text,
            file_name = os.path.basename(file_name), #os.path.basename(file_path),
            caption = caption,
            media_text = media_text,
        )

    except:
        raise Exception("Database error.")

    return media_object

def add_post(client_id, assignment_id, language_code, lat, lng, media_objects):

    post = None
    vote = None
    
    try:
        post = Posts.create_from_http(
            session = DBSession,
            client_id = client_id,
            assignment_id = assignment_id,
            #title = '', #title,
            language_code = language_code,
            lat = lat,
            lng = lng,
            media_objects = media_objects, # array
        )

        # register initial upvote from client
        vote = register_vote(
            post_id = post.post_id,
            client_id = client_id,
            is_up_vote = True
        )

    except:
        raise Exception("Database error.")

    return post, vote

def get_profile(client_id):

    post_count = 0
    
    try:

        post_count = Posts.get_count_from_client_id(
            session = DBSession,
            client_id = client_id,
        )

    except:
        raise Exception("Database error.")

    return post_count
