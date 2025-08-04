# what_to_watch/opinions_app/api_views.py
import string

from flask import jsonify, request

from . import app, db
from .constants import MAX_SHORT_LINK_LENGTH
from .error_handlers import InvalidAPIUsage
from .models import URLMap


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage("Отсутствует тело запроса", 400)
    if 'url' not in data:
        raise InvalidAPIUsage("\"url\" является обязательным полем!")
    if 'custom_id' in data:
        if len(data['custom_id']) >= MAX_SHORT_LINK_LENGTH:
            raise InvalidAPIUsage(
                "Указано недопустимое имя для короткой ссылки"
            )
        if URLMap.query.filter_by(short=data['custom_id']).first():
            raise InvalidAPIUsage(
                "Предложенный вариант короткой ссылки уже существует."
            )
        for symbol in data['custom_id']:
            if symbol not in (string.ascii_letters + string.digits):
                raise InvalidAPIUsage(
                    "Указано недопустимое имя для короткой ссылки"
                )
    link_object = URLMap()
    link_object.from_dict(data)
    db.session.add(link_object)
    db.session.commit()
    return jsonify({
        'url': link_object.original,
        'short_link': f"{request.host_url.rstrip('/')}/{link_object.short}"
    }), 201


@app.route('/api/id/<string:short_id>/')
def get_original_link(short_id):
    link_object = URLMap.query.filter_by(short=short_id).first()
    if not link_object:
        raise InvalidAPIUsage("Указанный id не найден", 404)
    return jsonify(link_object.to_dict_only_long()), 200
