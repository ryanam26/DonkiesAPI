from django.contrib.auth import get_user_model
from requests import request, HTTPError, post
from django.core.files.base import ContentFile
import json

User = get_user_model()
CLIENT_ID = 'ckXal1Ap3mPXiobaLq0hNwB8IHnCGexSNW6YHYBJ'
CLIENT_SECRET = 'dvAbRYxKZ7iQkNjN6lb7NwdmT7yaEddUOeALmI141WIO9L5EZTYdOjL1Hw4oMRetW3gBDECbDzlR7PztTOchhfvvkxzrjiEU5e2eU6jAy9mM91fkH7oxsUp5XaQeHrd3'

def create_or_update_user(backend, response, user=None, *args, **kwargs):

    if backend.name == 'facebook':
        # print('backend: %s' % backend)
        # print(('response: %s' % response))
        # print('args: %s' % str(args))
        # print('kwargs: %s' % str(kwargs))
        profile, created = User.objects.get_or_create(email=response.get('email'), fb_id=response.get('id'))
        if not created:
            curr_id = profile.fb_id
            returned_id = int(response.get('id'))
            assert (curr_id == returned_id), "Invalid user ID for provided email address."
        profile.first_name = response.get('first_name')
        profile.last_name = response.get('last_name')
        name = response.get('name')
        profile.gender = response.get('gender')
        profile.link = response.get('link')
        profile.timezone = response.get('timezone')
        profile.name = response.get('name')
        profile.age_range = json.dumps([response.get('age_range')])
        profile.birthday = response.get('birthday')
        profile.link = response.get('link')
        profile.gender = response.get('gender')
        profile.locale = response.get('locale')
        profile.user_timezone = response.get('timezone')
        profile.updated_time = response.get('updated_time')
        profile.verified = response.get('verified')

        img_url = response.get('picture').get('data').get('url')
        try:
            resp = request('GET', img_url, params={'fields': 'picture.height(961)'})
            resp.raise_for_status()
        except HTTPError:
            pass
        else:
            profile.picture.save('{0}_social.jpg'.format(name+str(profile.fb_id)),
                                 ContentFile(resp.content))

        profile.save()

        # data = {'grant_type': 'convert_token',
        #         'client_id': CLIENT_ID,
        #         'client_secret': CLIENT_SECRET,
        #         'backend': backend.name,
        #         'token': response.get('access_token')}
        # r = post('http://127.0.0.1:8000/auth/convert-token',
        #          data=data)
        # print(r.text)
        # r.raise_for_status()

        return {'user': profile}
