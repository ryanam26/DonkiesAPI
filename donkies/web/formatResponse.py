"""
Function for valid response

valid response shoul looks like
-in case Success

{
    "success": False,
    "errors": [
        {
            "code": { ...value },
            "message": { ...value },
        },
        {
            "code": { ...value },
            "message": { ...value },
        },
    ],

}

-in case Error:

{
    "success": True,
    "data": {
        "value": { ...value }
    }
}

In response arg should  pass {"errors": [...] }  or {}

"""


def format_response(response, status=None):

    if status >= 400:
        res = {
            "success": False,
            "errors": [],
        }

        if 'errors' in response and type(response['errors']) == list:
            for i in response['errors']:
                res['errors'].append({
                    'code': i['code'] if 'code' in i else '',
                    'message': i['message'] if 'message' in i else ''
                })
                print(res)

            return res

        res['errors'].append(response)

        return res

    res = {
        "success": True,
        "data": {
            "value": {}
        }
    }

    res['data'] = response

    return res
