# admin.py

from flask import Blueprint, request, g, redirect, url_for, abort, \
                  render_template

from flask.views import MethodView
from wtforms.ext.sqlalchemy.orm import model_form

from app import db

from .models import Blog, Comment

admin = Blueprint('admin', __name__, template_folder='templates')


class CRUDView(MethodView):
    list_template = 'admin/listview.html'
    detail_template = 'admin/detailview.html'

    def __init__(self, model, endpoint, list_template=None,
                 detail_template=None, exclude=None, filters=None):
        self.model = model
        self.endpoint = endpoint
        # so we can generate a url relevant to this
        # endpoint, for example if we utilize this CRUD object
        # to enpoint comments the path generated will be
        # /admin/comments/
        self.path = url_for('.%s' % self.endpoint)
        if list_template:
            self.list_template = list_template
        if detail_template:
            self.detail_template = detail_template
        self.filters = filters or {}
        self.ObjForm = model_form(self.model, db.session, exclude=exclude)


    def render_detail(self, **kwargs):
        return render_template(self.detail_template, path=self.path, **kwargs)

    def render_list(self, **kwargs):
        return render_template(self.list_template, path=self.path,
                               filters=self.filters, **kwargs)


    def get(self, obj_id='', operation='', filter_name=''):
        if operation == 'new':
            #  we just want an empty form
            form = self.ObjForm()
            action = self.path
            return self.render_detail(form=form, action=action)
            
        if operation == 'delete':
            obj = self.model.query.get(obj_id)
            db.session.delete(obj)
            db.session.commit()
            return redirect(self.path)

        # list view with filter
        if operation == 'filter':
            func = self.filters.get(filter_name)
            obj = func(self.model)
            return self.render_list(obj=obj, filter_name=filter_name)


        if obj_id:
            # this creates the form fields base on the model
            # so we don't have to do them one by one
            ObjForm = model_form(self.model, db.session)

            obj = self.model.query.get(obj_id)
            # populate the form with our blog data
            form = self.ObjForm(obj=obj)
            # action is the url that we will later use
            # to do post, the same url with obj_id in this case
            action = request.path
            return self.render_detail(form=form, action=action)

        obj = self.model.query.order_by(self.model.created_on.desc()).all()
        return self.render_list(obj=obj)

    def post(self, obj_id=''):
        # either load and object to update if obj_id is given
        # else initiate a new object, this will be helpfull
        # when we want to create a new object instead of just
        # editing existing one
        if obj_id:
            obj = self.model.query.get(obj_id)
        else:
            obj = self.model()

        ObjForm = model_form(self.model, db.session)
        # populate the form with the request data
        form = self.ObjForm(request.form)
        # this actually populates the obj (the blog post)
        # from the form, that we have populated from the request post
        form.populate_obj(obj)

        db.session.add(obj)
        db.session.commit()

        return redirect(self.path)



# def dec(f):
#     def decorated(*args, **kwargs):
#         print 'run decorator run'
#         return f(*args, **kwargs)
#     return decorated

blog_filters = {
'created_asc': lambda model: model.query.order_by(model.created_on.asc()),
'updated_desc': lambda model: model.query.order_by(model.updated_on.desc()),
'last_3': lambda model: model.query.order_by(model.created_on.desc()).limit(3)
}


# view = CRUDView.as_view('blog', Blog, endpoint='blog', filters=filters)
# # view = CRUDView.as_view('blog', Blog, endpoint='blog', decorators=[dec])
# admin.add_url_rule('/blog/', view_func=view, methods=['GET', 'POST'])
# admin.add_url_rule('/blog/<operation>/', view_func=view, methods=['GET'])
# admin.add_url_rule('/blog/<operation>/<int:obj_id>/', view_func=view,
#                    methods=['GET'])
# admin.add_url_rule('/blog/<int:obj_id>/', view_func=view,
#                    methods=['GET', 'POST'])
# admin.add_url_rule('/blog/<operation>/<filter_name>/', view_func=view,
#                     methods=['GET'])


def register_crud(app, url, endpoint, model, decorators=[], **kwargs):
    view = CRUDView.as_view(endpoint, endpoint=endpoint,
                            model=model, **kwargs)

    for decorator in decorators:
        view = decorator(view)

    app.add_url_rule('%s/' % url, view_func=view, methods=['GET', 'POST'])
    app.add_url_rule('%s/<int:obj_id>/' % url, view_func=view)
    app.add_url_rule('%s/<operation>/' % url, view_func=view, methods=['GET'])
    app.add_url_rule('%s/<operation>/<int:obj_id>/' % url, view_func=view,
                     methods=['GET'])
    app.add_url_rule('%s/<operation>/<filter_name>/' % url, view_func=view,
                     methods=['GET'])


comment_filters = {
        'invisible': lambda model: model.query.filter_by(visible=False).all(),
        'visible': lambda model: model.query.filter_by(visible=True).all()
    }


register_crud(admin, '/blog', 'blog', Blog, filters=blog_filters)
register_crud(admin, '/comments', 'comments', Comment, filters=comment_filters)