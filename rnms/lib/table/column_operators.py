
from sqlalchemy.sql.operators import ColumnOperators as coop

COL_OPERATORS = {
    'eq':   (coop.__eq__, False),
    'ne':   (coop.__ne__, False),
    'bw':   (coop.startswith, False),
    'bn':   (coop.startswith, True),
    'ew':   (coop.endswith, False),
    'en':   (coop.endswith, True),
    'cn':   (coop.contains, False),
    'nc':   (coop.contains, True),
}
