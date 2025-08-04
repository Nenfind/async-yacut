from flask import redirect, render_template

from . import app, db
from .forms import FilesForm, LinksForm
from .models import URLMap
from .yandex_disk import async_upload_files_to_yadisk


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = LinksForm()
    if form.validate_on_submit():
        try:
            url_map = URLMap.validate_and_create(
                original_link=form.original_link.data,
                short_link=form.custom_id.data if form.custom_id.data else None
            )
            return render_template(
                'index.html',
                form=form,
                short_link=url_map.short
            )
        except ValueError as e:
            db.session.rollback()
            form.custom_id.errors.append(str(e))
    return render_template('index.html', form=form)


@app.route('/<string:short_link>')
def redirect_view(short_link):
    object = URLMap.query.filter_by(short=short_link).first_or_404()
    return redirect(object.original, code=302)


@app.route('/files', methods=['GET', 'POST'])
async def files_view():
    form = FilesForm()
    if form.validate_on_submit():
        yadisk_urls = await async_upload_files_to_yadisk(form.files.data)
        file_info = []
        for url, file in zip(yadisk_urls, form.files.data):
            new_link = URLMap(
                original=url,
            )
            db.session.add(new_link)
            db.session.flush()
            file_info.append({
                'short': new_link.short,
                'filename': file.filename,
            })
        db.session.commit()
        return render_template('files.html', form=form, file_info=file_info)
    return render_template('files.html', form=form)
