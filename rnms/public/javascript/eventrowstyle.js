function eventRowStyle(value, row, index)
{
	if (value['severity_id'] == 1) {
		return false;
	}
	return { classes: 'severity'+value['severity_id']}; 
}
