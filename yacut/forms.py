from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, ValidationError

from .models import URLMap


class LinksForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[Length(
            0,
            16,
            message='Ссылка должна быть не длиннее 16 символов'
        ),
        ]
    )
    submit = SubmitField('Создать')

    def validate_custom_id(self, field):
        if field.data:
            if (
                field.data == 'files' or
                URLMap.query.filter_by(short=field.data).first()
            ):
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )


class FilesForm(FlaskForm):
    files = MultipleFileField(
        'Выберите файлы',
        validators=[DataRequired(message='Выберите хотя бы один файл')]
    )
    submit = SubmitField('Создать')
