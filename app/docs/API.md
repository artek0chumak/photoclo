# API
### Authorization:
* /api/sign_in/ - sign in account, requires username and password.
    * POST: username and password
        * HTTP\_CODE: 200 - STATUS: OK, return token in data.
        * HTTP\_CODE: 400 - STATUS: error BAD\_REQUEST, no username or password.
        * HTTP\_CODE: 404 - STATUS: error NOT\_FOUND, username or password are incorrect.
        * Example of return: `{data: {token: ....}}`
* /api/sign_up/ - sign up account, requires username, email and password.
    * POST: username, password and email
        * HTTP\_CODE: 200 - STATUS: OK, return token in data.
        * HTTP\_CODE: 400 - STATUS: error BAD\_REQUEST, no username, password or email.
        * HTTP\_CODE: 409 - STATUS: error CONFLICT, user with this username already exists.
        * HTTP\_CODE: 500 - STATUS: error INTERNAL\_SERVER\_ERROR, error in saving user, it don't relate with usernames conflict.
        * Example of return: `{data: {token: ....}}`
* /api/sign_out/ - sign out account. If there is no open session, return HTTP code 200.
    * POST: nothing
        * HTTP\_CODE: 200 - STATUS: OK, return nothing.
### Photos:
* For all urls:
    * HTTP\_CODE: 401 - error UNAUTHORIZED - user is not authorized.
* /api/photos/ - return photos
    * GET: offset, limit and size
        * HTTP\_CODE: 200 - STATUS: OK, return amount of photos in `count` and list of photos in needed size, where is heights, width, urls and id.
        * HTTP\_CODE: 400 - STATUS: error BAD\_REQUEST, no limit, offset or size was sent, return error with description:
            * "Offset is too large" - offset is larger than amount of photos in a server.
            * "" - other errors.
        * Example of return: `{ data: {count: 10, photos: [{id: 10, urls: /media/.../image1.jpeg, height: 1080, width: 920}, ...]}}`, 
    * POST: photo
        * HTTP\_CODE: 201 - STATUS: OK, return list with status of photos:
            * 'Success' - photo was loaded and saved.
            * 'Fail' - photo wasn't loaded or saved.
        * HTTP\_CODE: 500 - STATUS: error INTERNAL\_SERVER\_ERROR, error not in the saving process.
* /api/photos/\<id\>/ - open or delete photo by id.
    * GET: nothing
        * HTTP\_CODE: 200 - STATUS: OK, return url for full-size photo.
        * HTTP\_CODE: 404 - STATUS: error NOT\_FOUND, there is no photo with this id.
        * Example of return: `{ data: {url: /media/.../image.jpeg}}`
    * DELETE: nothing
        * HTTP\_CODE: 200 - STATUS: OK, return nothing.
        * HTTP\_CODE: 404 - STATUS: error NOT\_FOUND, there is no photo with this id.
* /api/photos/\<id\>/download/ - download photos by id.
    * GET: nothing
        * HTTP\_CODE: 200 - STATUS: OK, return url to download original and type('Yandex' or 'Photoclo').
        * HTTP\_CODE: 404 - STATUS: error NOT\_FOUND, there is no photo with this id.
        * Example of  return: `{'url': 'https://downloader.dst.yandex.ru/disk/...',
        'type': 'Yandex''}`
### Faces and avatars:
* For all urls:
    * HTTP\_CODE: 401 - error UNAUTHORIZED - user in not authorized.
* /api/faces/\<id\>/ - return faces on photo or edit face. \<id\> - photo id.
    * GET: nothing    
        * HTTP\_CODE: 200 - STATUS: OK, return faces on photo in `faces`.
        * HTTP\_CODE: 204 - STATUS: NO\_CONTENT, faces don't exist.
        * Example of return: `{ "faces": [{ "id": 1, "avatar": 2, "photo": 15, "embedding": [0.9124, 0.1982, ..., 0.5233]}, "bounding_box": [131, 168, 343, 438], "user_checked": False },...]}`,
        in bounding boxes points (x1, y1), (x2, y2) of box on original-size photo; x1 < x2, y1 < y2. `avatar` is id of probable avatar, if `user_checked` is True then `avatar` was set or checked by user.
    * PUT: face id and new avatar id
        * HTTP\_CODE: 200 - STATUS: OK, return new face.
        * HTTP\_CODE: 404 - STATUS: error NOT\_FOUND, face with this id wasn't found.
        * Example of request: `{ "face": 1, "new_avatar": 4}`, `face` - face id, `new_avatar` - avatar id.
        * Example of return: `{ "new_face": {"id": 1, "avatar": 4, "photo": 15, "embedding": [0.9124, 0.1982, ..., 0.5233]}, "bounding_box": [131, 168, 343, 438], "user_checked": False }}`
* /api/faces/\<id\>/suggest/ - return suggestion avatars for faces in photo. \<id\> - photo id.
    * GET: `query` - string by user. It can be empty.
        * HTTP\_CODE: 200 - STATUS: OK, return probable avatars, if query was empty, or avatars contains query in name
        * Example of return: after empty query `{'avatars': [{'face': 2, 'avatar': 5, 'avatar_name': Mama, 'place': 1},...]}`, place is confidence of photo own to avatar: 1 - the most, 5 - the less.
        * Example of return: after nonempty query `{'avatars': [{'id': 5, 'name': Father},...]}`
* /api/avatars/ - create avatar or return list of avatars
    * GET: nothing
        * HTTP\_CODE: 200 - STATUS: OK, return avatars in `avatars`.
        * HTTP\_CODE: 204 - STATUS: NO\_CONTENT, avatars don't exist.
        * Example of return: `{ "avatars": [{"id": 1, "name": 'New Avatar'}, ...]}`
    * POST: face_id and avatar name
        * HTTP\_CODE: 201 - STATUS: CREATED, return created avatar.
        * HTTP\_CODE: 500 - STATUS: error INTERNAL\_SERVER\_ERROR, error in creating avatar.
        * Example of request: `{ "face_id": 1, "name": 'Mother'}`
        * Example of return: `{ "id": 4, "name": 'Mother'}`, `id` - avatar id, `name` - avatar new name.
* /api/avatars/\<id\>/ - update avatars. \<id\> - avatar id.
    * PATCH: new name
        * HTTP\_CODE: 200 - STATUS: OK, avatar name was changed
        * HTTP\_CODE: 404 -  STATUS: error NOT\_FOUND, avatar with this id wasn't found.
        * Example of request: `{ "new_name": 'Father', "face": 3}}`
        * Example of return: `{"updated_avatar": {"id": 5, "name": 'Father'}}`, `id` - avatar id, `name` - avatar new name.
* /api/avatars/\<id\>/photos/ - return list of photos, \<id\> - avatar id.
    * GET: nothing
        * HTTP\_CODE: 200 - STATUS: OK, return list of photos.
        * HTTP\_CODE: 204 - STATUS: NO\_CONTENT, nothing to show.
        * Example of return: `{"photos":[{"owner":2,"storage":{"id":2,"original":"/media/54939d45b7fa40f3b6e3f2c539131c2f/image.jpeg"},"width":6016,"height":4000},...]`
### Yandex Disk
* /api/tokens/code/ - return url for user to add app access to his disk.
    * GET: nothing
        * HTTP\_CODE: 200 - STATUS: OK, return url. If user gives access, return nothing.
        * Example of return: `{
    "url": "https://oauth.yandex.ru/authorize?response_type=code&client_id=..."
}`
* /api/tokens/status/ - check that user added Yandex Disk access.
    * GET: nothing
        * HTTP\_CODE: 200 - STATUS: OK, return `{'sync': True}`
        * HTTP\_CODE: 204 - STATUS: NO\_CONTENT, return `{'sync': False}`
* /api/cloud-status/\<id\> - check photo status. \<id\> - photo id
    