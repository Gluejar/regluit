function imgblur(pos){
	if (document.getElementById('watermark').value == "") {
		document.getElementById('watermark').style.background="white url('/static/images/google_watermark.gif') no-repeat "+pos+"px center";
	}
}

function imgfocus(){
	document.getElementById('watermark').style.background="";
}
