import random
import string
from datetime import datetime
from sqlite3 import IntegrityError

from sqlalchemy import event, select

from yacut import db
from yacut.constants import (
    MAX_SHORT_LINK_LENGTH,
    MAX_SHORT_LINK_LENGTH_GENERATED
)


def get_unique_short_id(length=MAX_SHORT_LINK_LENGTH_GENERATED):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String, nullable=False)
    short = db.Column(
        db.String(MAX_SHORT_LINK_LENGTH),
        nullable=False,
        unique=True
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def to_dict_only_long(short_link=None):
        if short_link:
            url_map = URLMap.query.filter_by(short=short_link).first()
            if url_map:
                return {
                    'url': url_map.original
                }
            else:
                raise ValueError("Указанный id не найден")

    @staticmethod
    def validate_and_create(original_link, short_link=None):
        if short_link:
            if len(short_link) > MAX_SHORT_LINK_LENGTH:
                raise ValueError(
                    'Указано недопустимое имя для короткой ссылки'
                )
            if URLMap.query.filter_by(short=short_link).first():
                raise ValueError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
            # if not all(
            #         c in (string.ascii_letters + string.digits)
            #         for c in short_link
            # ):
            #     raise ValueError(
            #         "Указано недопустимое имя для короткой ссылки"
            #     )
            not_valid_chars = []
            for char in short_link:
                if char not in (string.ascii_letters + string.digits):
                    not_valid_chars.append(char)
            if len(not_valid_chars) > 0:
                raise ValueError(
                    'Эти символы нельзя использовать: '
                    f'{", ".join(set(not_valid_chars))} '
                )

        url_map = URLMap(original=original_link, short=short_link)
        db.session.add(url_map)
        try:
            db.session.commit()
            return url_map
        except IntegrityError:
            db.session.rollback()
            raise ValueError(
                'Произошла ошибка при создании ссылки.'
                'Пожалуйста, попробуйте другой вариант.')


@event.listens_for(URLMap, 'before_insert')
def generate_short_if_missing(mapper, connection, target):
    """
    Auto-generate short link just before database insert
    if it was not provided by user.
    """
    if not target.short:
        while True:
            short_link = get_unique_short_id()
            exists = connection.execute(
                select(URLMap.id).where(URLMap.short == short_link).limit(1)
            ).scalar()
            if not exists:
                target.short = short_link
                break
