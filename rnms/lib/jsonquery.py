
import operator
from sqlalchemy import and_, not_

def op_starts_with(x,y): return x.startswith(y)
def op_starts_notwith(x,y): return not_(x.startswith(y))
def op_ends_with(x,y): return x.endswith(y)
def op_ends_notwith(x,y): return not_(x.endswith(y))
def op_contains(x,y): return x.contains(y)
def op_not_contains(x,y): return not_(x.contains(y))
def op_isnull(x,y): return x.is_()
def op_isnotnull(x,y): return x.isnot()
def op_isin(x,y):
    vals = y.split(',')
    return x.in_(vals)
def op_isnotin(x,y): return not_(op_isin(x,y))

query_operators = {
        'eq': operator.eq,
        'ne': operator.ne,  
        'bw': op_starts_with,
        'bn': op_starts_notwith,
        'ew': op_ends_with,
        'en': op_ends_notwith,
        'cn': op_contains,
        'nc': op_not_contains,
        'nu': op_isnull,
        'nn': op_isnotnull,
        'in': op_isin,
        'ni': op_isnotin,
        }

def json_query(qry, colnames, page, rows, sidx, sord, _search, searchOper, searchField, searchString):
    """ 
    Returns the database rows for the given query, used for the griddata
    methods out of the controllers
    """
    conditions = []
    order_field = None
    if _search == True or sidx is not None:
        for c in colnames:
            if _search == True and c[0] == searchField:
                conditions.append(query_operators[searchOper](c[1], searchString))
                if sidx is None or order_field is not None:
                    break
            if c[0] == sidx:
                if sord == 'asc':
                    order_field = c[1]
                else:
                    order_field = c[1].desc()
                if _search == False or conditions != []:
                    break

    qry = qry.filter(and_(*conditions)).order_by(order_field)
    result_count = qry.count()
    offset = (page-1) * rows
    qry = qry.offset(offset).limit(rows)
    if sidx is not None:
        pass
    print 'sort',sidx,sord
    return result_count, qry



