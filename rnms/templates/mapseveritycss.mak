/*
 * CSS Stylesheet for the Map Widget - used to dynamically display the
 * map items in different colours
 */
.maplist li.mapseverityok {
	color: #00ff00;
    border-color: #00ff00;
	background-color: #003f00;
}

.maplist li.mapseverityasd {
	color: #cccccc
    border-color: #cccccc;
	background-color: #333333;
}


%for severity in severities:
.maplist li.mapseverity${severity[0]} {
    color: #${severity[1]};
	border-color: #${severity[1]};
    background-color: #${severity[2]};
}
%endfor
