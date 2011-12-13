function imgblur(pos){
	if (document.getElementById('watermark').value == "") {
		document.getElementById('watermark').style.background="white url('/static/images/google_watermark.gif') no-repeat "+pos+"px center";
	}
}

function imgfocus(){
	document.getElementById('watermark').style.background="";
}

// special case for search box which is repeated on empty search results page
function imgblurempty(pos){
	if (document.getElementById('watermarkempty').value == "") {
		document.getElementById('watermarkempty').style.background="white url('/static/images/google_watermark.gif') no-repeat "+pos+"px center";
	}
}

function imgfocusempty(){
	document.getElementById('watermarkempty').style.background="";
}
