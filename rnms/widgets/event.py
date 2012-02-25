import tg
import tw2.core as twc
from rnms.model import DBSession, Event
from sqlalchemy import select,func,or_

class EventsWidget(twc.Widget):
    id = 'events-widget'
    template = 'rnms.templates.eventswidget'

    host = twc.Param('Limit events by this host id')
    event_type = twc.Param('Limit events by this event_type id')

    def prepare(self):
        from webhelpers import paginate
        conditions = []
        copy_args = {}
        if hasattr(self, 'host'):
            host_id = getattr(self, 'host')
            if type(host_id) <> int:
                raise ValueError, "Host ID must be an integer"
            conditions.append(Event.host_id==host_id)
            copy_args['h']=1
        condition = or_(*conditions)
        events = DBSession.query(Event).filter(condition).order_by(Event.id.desc())
        count = events.count()
        page = int(getattr(self, 'page', '1'))
        span = int(getattr(self, 'span', '20'))
        self.currentPage = paginate.Page(
                events, page, item_count=count,
                items_per_page=span,
                )
        #for arg in copy_args:
        #    self.currentPage.kwargs[arg] = str(kw[arg])
        
        self.events = self.currentPage.items
        self.tgurl = tg.url
        super(EventsWidget, self).prepare
