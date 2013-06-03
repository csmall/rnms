
from tg.predicates import has_permission, Any
host_ro = Any(has_permission('HostRO'), has_permission('HostRW'),
              msg='User must have Host View permissions')

host_rw = has_permission('HostRW',
              msg='User must have Host Admin permissions')
             
