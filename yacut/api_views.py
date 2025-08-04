# what_to_watch/opinions_app/api_views.py

from flask import jsonify, request

from . import app
from .error_handlers import InvalidAPIUsage
from .models import URLMap


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage("Отсутствует тело запроса", 400)
    if 'url' not in data:
        raise InvalidAPIUsage("\"url\" является обязательным полем!")
    try:
        url_map = URLMap.validate_and_create(
            original_link=data['url'],
            short_link=data.get('custom_id')
        )
        return jsonify({
            'url': url_map.original,
            'short_link': f"{request.host_url.rstrip('/')}/{url_map.short}"
        }), 201
    except ValueError as e:
        raise InvalidAPIUsage(str(e), 400)


@app.route('/api/id/<string:short_id>/')
def get_original_link(short_id):
    try:
        long_link = URLMap.to_dict_only_long(short_id)
    except ValueError as e:
        raise InvalidAPIUsage(str(e), 404)
    return jsonify(long_link), 200
