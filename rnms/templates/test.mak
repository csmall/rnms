<%inherit file="local:templates.master"/>
	blah
	${text}
${mm.display(page=page) | n}
<img id="testimg" src="/images/turbogears_logo.png">

<button id="pressbtn" class="btn">Press</button>

<script>
$("#pressbtn").click(function() { alert("Clicked!"); $("#testimg").attr("src", "/images/under_the_hood_blue.png"); });
</script>
