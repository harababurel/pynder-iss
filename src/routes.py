from main import app
from view import IndexView, ChatView, MatchesView, SwipeView, VoteView, StatisticsView, LoginView, SettingsView, \
    LogoutView, MessagesView, UnmatchView

statistics_view_func = StatisticsView.as_view('statistics')

app.add_url_rule('/', view_func=IndexView.as_view('index'))
app.add_url_rule('/chat', view_func=ChatView.as_view('chat'), defaults={'user_id': None}, methods=['POST'])
app.add_url_rule('/matches', view_func=MatchesView.as_view('matches'))
app.add_url_rule('/swipe', view_func=SwipeView.as_view('swipe'))
app.add_url_rule('/vote', view_func=VoteView.as_view('vote'), methods=['POST'])
app.add_url_rule('/statistics/<category>', view_func=statistics_view_func)
app.add_url_rule('/statistics/', view_func=statistics_view_func, defaults={'category': 'general'})
app.add_url_rule('/login', view_func=LoginView.as_view('login'), methods=['GET', 'POST'])
app.add_url_rule('/settings', view_func=SettingsView.as_view('settings'), methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
app.add_url_rule('/messages', view_func=MessagesView.as_view('messages'), methods=['POST'])
app.add_url_rule('/unmatch/<id>', view_func=UnmatchView.as_view('unmatch'), methods=['POST'])


@app.errorhandler(404)
def page_not_found(error):
    return "page not found", 404
