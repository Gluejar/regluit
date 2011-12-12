function imgblur(){
	if (document.getElementById('watermark').value == "") {
		document.getElementById('watermark').style.background="url('/static/images/google_watermark.gif') no-repeat left center";
	}
}

function imgfocus(){
	document.getElementById('watermark').style.background="";
}
