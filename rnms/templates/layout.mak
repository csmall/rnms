<%namespace name="tw" module="tw2.core.mako_util"/>
<div >
	% for entry in w.children:
		${entry.display() | n }
	% endfor
</div>
