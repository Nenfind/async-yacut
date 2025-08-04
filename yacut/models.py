import random
import string
from datetime import datetime

from sqlalchemy import event, select

from yacut import db
from yacut.constants import MAX_SHORT_LINK_LENGTH


def get_unique_short_id(length=6):
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

    def to_dict_only_long(self):
        return {
            'url': self.original,
        }

    def from_dict(self, data):
        self.original = data['url']
        if 'custom_id' in data:
            self.short = data['custom_id']


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
