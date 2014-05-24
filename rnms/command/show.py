
from cliff.command import Command
from rnms import model


class Show(Command):
    """ Command that shows information on certain models """

    def get_parser(self, prog_name):
        query_types = list(x[:-5] for x in dir(self) if x[-5:] == '_info')
        parser = super(Show, self).get_parser(prog_name)
        parser.add_argument(
            action='store',
            dest='qtype',
            type=str,
            choices=query_types,
            help='Query Type:' + ', '.join(query_types),
            metavar='<query type>')
        parser.add_argument(
            action='store',
            dest='ids',
            type=int,
            metavar='ID',
            nargs='+',
            help='IDs of the object to show',
        )

        return parser

    def take_action(self, parsed_args):
        try:
            real_info = getattr(self, parsed_args.qtype+'_info')
        except AttributeError:
            raise RuntimeError(
                'Unknown query type "{}".'.format(parsed_args.qtype))
        real_info(parsed_args.ids)

    def attribute_info(self, ids):
        attributes = self._get_objects(model.Attribute, 'Attributes', ids)
        if attributes is None:
            return
        print
        for attribute in attributes:
            self.line('=')
            print '{:<20} | {}: {} (index: {})'.format(
                'Attribute', attribute.id,
                attribute.display_name, attribute.index)
            self.line('-')
            print """{:<20} | {}: {}
{:<20} | {}/{}
{:<20} | {}: {}
{:<20} | {}: {} (enabled:{})
{:<20} | {}
{:<20} | {}: {}
{:<20} | {}
{:<20} | {}
{:<20} | {}""".format(
                'Host', attribute.host.id, attribute.host.display_name,
                'State (admin/oper)', attribute.admin_state_name(),
                attribute.oper_state,
                'Attribute Type', attribute.attribute_type.id,
                attribute.attribute_type.display_name,
                'Poller Set', attribute.poller_set.id,
                attribute.poller_set.display_name, attribute.poll_enabled,
                'Poll Priority', attribute.poll_priority,
                'SLA', attribute.sla.id, attribute.sla.display_name,
                'Created', attribute.created,
                'Next SLA', attribute.next_sla,
                'Next Poll', attribute.next_poll)
            self.line('-')
            print 'Fields'
            for field in attribute.fields:
                at_field = model.AttributeTypeField.by_id(
                    field.attribute_type_field_id)
                print '{:<20} | {}'.format(at_field.display_name, field.value)
        self.line('=')

    def pollerset_info(self, ids):
        poller_sets = self._get_objects(model.PollerSet, 'Poller Sets', ids)
        if poller_sets is None:
            return
        print
        for poller_set in poller_sets:
            self.line('=')
            print 'Poller Set          | {}: {}'.format(
                poller_set.id, poller_set.display_name)
            self.line('-')
            print '''{:<20} | {}:{}
            '''.format(
                'Attribute Type', poller_set.attribute_type_id,
                poller_set.attribute_type.display_name,
                )
            self.line('-')
            print 'Poller Rows\nPos| {:<39} | {:<29}'.\
                format('Poller', 'Backend')
            for row in poller_set.poller_rows:
                print '{:<3}| {:<3}:{:<35} | {:<3}:{:<25}'.format(
                    row.position,
                    row.poller_id,
                    (row.poller.display_name+' ('+row.poller.command+')')[:35],
                    row.backend_id,
                    (row.backend.display_name +
                        ' ('+row.backend.command+')')[:25],
                    )
        print '=' * 60

    def autodiscovery_info(self, ids):
        """ Information about the autodiscovery policy """
        policies = self._get_objects(
            model.AutodiscoveryPolicy, 'Autodiscovery Policies', ids)
        if policies is None:
            return
        print
        for policy in policies:
            self.line('=')
            print '{:<30} | {}: {}'.format('Autodiscovery Policy', policy.id,
                                           policy.display_name)
            self.line('-')
            print '''Autodiscovery will not examine attribute if it:
{:<30} | {}
{:<30} | {}
{:<30} | {}

Attribute Autodiscovery can do the following:
{:<30} | {}
{:<30} | {}
{:<30} | {}
{:<30} | {}
{:<30} | {}
            '''.format(
                    ' - is a Loopback', policy.skip_loopback,
                    ' - is Oper Down', policy.check_state,
                    ' - has no address', policy.check_address,
                    ' - set the PollerSet', policy.set_poller,
                    ' - add new attributes', policy.permit_add,
                    ' - disable missing attributes', policy.permit_disable,
                    ' - delete missing attributes ', policy.permit_delete,
                    ' - alert on missing attributes', policy.alert_delete,
                    ' - modify attribute fields', policy.permit_modify,
                )

    def _parse_sysobjid(self, sysobjid):
        if sysobjid is None or sysobjid == '':
            return 'No SNMP required'
        elif sysobjid == '.':
            return 'All SNMP enabled hosts'
        return 'sysObjectId=' + sysobjid

    def atype_info(self, ids):
        """ Information about the attribute types """
        atypes = self._get_objects(model.AttributeType, 'Attribute Types', ids)
        if atypes is None:
            return
        print
        for atype in atypes:
            self.line('=')
            print '{:<30} | {}: {}'.format('Attribute Type', atype.id,
                                           atype.display_name)
            self.line('-')
            print '''{:<30} | (enabled: {})
{:<30} | {}
{:<30} | {}
{:<30} | {}({})
{:<30} | {}: {}
{:<30} | {}: {}
{:<30} | Heatbeat: {} CF: {} Rows: {}
'''.format(
                'Autodiscovery', atype.ad_enabled,
                'Required Host SNMP',
                self._parse_sysobjid(atype.required_sysobjid),
                'Validate', atype.ad_validate,
                'Command', atype.ad_command, atype.ad_parameters,
                'Default PollerSet', atype.default_poller_set_id,
                atype.default_poller_set.display_name,
                'Default SLA', atype.default_sla_id,
                atype.default_sla.display_name,
                'RRA Info', atype.ds_heartbeat, atype.rra_cf, atype.rra_rows,
                )
            self.line('-')
            print 'Fields'
            for field in atype.fields:
                print '{:<3} {:<26} | tag:{}'.format(
                    field.position, field.display_name, field.tag)
            self.line('-')
            print 'RRDtool files'
            for rrd in atype.rrds:
                print '{:<3} {:<26} | {:<5} {}'.format(
                    rrd.position, rrd.display_name, rrd.dst2str(), rrd.name)

    def sla_info(self, ids):
        """ Information about SLAs """
        slas = self._get_objects(model.Sla, 'SLAs', ids)
        if slas is None:
            return
        print
        for sla in slas:
            try:
                at_name = sla.attribute_type.display_name
            except AttributeError:
                at_name = 'None'
            self.line('=')
            print '{:<30} | {}: {}'.format('SLA', sla.id, sla.display_name)
            self.line('-')
            print '''{:<30} | {}: {}
{:<30} | {}% '''.format( 'Attribute Type', sla.attribute_type_id, at_name,
        'Threshold', sla.threshold,
        )
            self.line('-')
            print 'Rules\nPos| {:>40} | Oper| Limit'.format('Expression')
            self.line('-')
            for row in sla.sla_rows:
                print '{:<3}| {:>40} | {:>3} | {:<8}'.format(
                        row.position, 
                        row.expression[:40], row.oper, row.limit
                        )
                expr_len = len(row.expression)
                for idx in range(40,256,40):
                    if expr_len > idx:
                        print '   | {:>40} |     |'.format(
                            row.expression[idx:idx+40])

        print '=' * 60

    def trap_info(self, ids):
        """ Information about SNMP traps """
        traps = self._get_objects(model.SnmpTrap, 'Traps', ids)
        if traps is None:
            return
        print
        for trap in traps:
            self.line('=')
            print '''{:<30} | {}
{:<30} | {}: {}
{:<30} | {}
{:<30} | {}'''.format(
                'Trap', trap.id,
                'Host', trap.host.id, trap.host.display_name,
                'Trap OID', trap.trap_oid,
                'Processed', trap.processed
                )
            self.line('-')
            print 'Varbinds'
            for varbind in trap.varbinds:
                if varbind.oid == '1.3.6.1.2.1.1.3.0':
                    try:
                        uptime = datetime.timedelta(seconds=int(varbind.value))
                    except (ValueError, TypeError):
                        uptime = '???'
                    print '{:<40} = {} ({}s)'.format(
                        'System Uptime', uptime, varbind.value)
                    continue
                elif varbind.oid == '1.3.6.1.6.3.1.1.4.3.0':
                    oid = 'Enterprise'
                else:
                    oid = varbind.oid
                if varbind.value[:12] == '1.3.6.1.4.1.':
                    ent, device = model.SNMPEnterprise.oid2name(varbind.value)
                    value = '{} - {} ({})'.format(
                        ent, device, varbind.value)
                else:
                    value = varbind.value

                print '{:<40} = {}'.format(oid, value)

    def trigger_info(self, ids):
        """ Information about the triggers """
        triggers = self._get_objects(model.Trigger, 'Triggers', ids)
        if triggers is None:
            return
        print
        for trigger in triggers:
            self.line('=')
            print '''{:<30} | {}: {}
{:<30} | {}
{:<30} | {} - {}'''.format('Trigger', trigger.id, trigger.display_name,
        'Match Type', trigger.match_type_name().capitalize(),
        'Email: Owner - Users', trigger.email_owner, trigger.email_users,
        )
            self.line('-')
            print 'Rules'
            for rule in trigger.rules:
                stop = rule.stop and 'STOP' or 'CONTINUE'
                andor = rule.and_rule and 'AND' or 'OR'
                print '{}: {} {} {} ({} - {})'.format(
                    rule.position, rule.field_name(), rule.oper, rule.limit,
                    andor, stop)

    def host_info(self, ids):
        hosts = self._get_objects(model.Host, 'Hosts', ids)
        if hosts is None:
            return
        print
        for host in hosts:
            self.line('=')
            print '{:<20} | {}: {}'.format('Host', host.id, host.display_name)
            self.line('-')
            print '''{:<20} | {}: {}
{:<20} | {}
{:<20} | {}
{:<20} | {} / {}
{:<20} | {} : {}
{:<20} | {}
{:<20} | {}
{:<20} | {}
{:<20} | ({}) {}'''.format(
                'Zone', host.zone.id, host.zone.display_name,
                'Management IP', host.mgmt_address,
                'System ObjID', host.sysobjid,
                'Community RO/RW', host.ro_community.display_name,
                host.rw_community.display_name,
                'Autodiscovery', host.autodiscovery_policy.id,
                host.autodiscovery_policy.display_name,
                'Config Backup', host.config_backup_method.display_name,
                'Created', host.created,
                'Next Discovery', host.next_discover,
                'Attributes', len(host.attributes), ', '.join(
                    [str(a.id)+('', '(P)')[a.poll_priority]
                        for a in host.attributes])
                )

    def _get_objects(self, db_table, description, ids):
        obj = model.DBSession.query(db_table).filter(
            db_table.id.in_(ids))
        if obj.count() == 0:
            print "No {} found".format(description)
            return None
        return obj

    def line(self, char):
        print char * 60
