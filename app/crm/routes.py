import typing



if typing.TYPE_CHECKING:
    from app.web.app import Application

def setup_routes(app):
    from app.crm.views import AddNewJokeView
    from app.crm.views import AddNewTopicView
    from app.crm.views import ListAllTopicView
    from app.crm.views import DeleteJokeView
    from app.crm.views import GetJokeView
    from app.crm.views import AddNewUserView
    from app.crm.views import LoginView
    from app.crm.views import GetUsersView

    app.router.add_view('/topics', AddNewTopicView )
    app.router.add_view('/joke', AddNewJokeView)
    app.router.add_view('/get_topics',ListAllTopicView )
    app.router.add_view('/joke/{joke_id}', DeleteJokeView )
    app.router.add_view('/get_joke', GetJokeView)
    app.router.add_view('/register_user', AddNewUserView)
    app.router.add_view('/login', LoginView)
    app.router.add_view('/get_user', GetUsersView)