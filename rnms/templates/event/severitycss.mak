%for severity in severities:

.severity${severity.id} {
    color: #${severity.fgcolor};
    background-color: #${severity.bgcolor};
}
	 %endfor
