%for severity in severities:

.maplist li.mapseverity0 {
	color: #00ff00;
border-color: #00ff00;
	background-color: #003f00;
}

.maplist li.mapseverity${severity[0]} {
    color: #${severity[1]};
	border-color: #${severity[1]};
background-color: #${severity[2]};
}
	 %endfor
