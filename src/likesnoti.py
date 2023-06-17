import src.models as models


def get_scheme_like_ws(like: models.Like):
    print(like)
    data = {
        'id': like.id,
        'user_id': like.user_id,
        'post_id': like.post_id,
        'type': 'like',
        'profile': {
            'id': like.user_id,
            'name': like.profile.name,
            'surname': like.profile.surname,
            'tag_name': like.profile.tag_name
        },
        'post': {
            'profile_id': like.posts.profile_id
        }
    }
    return data
