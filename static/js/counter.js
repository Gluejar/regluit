function counter(textarea, maxLen){
	count = document.getElementById('count_display');
	if (textarea.value.length > maxLen) {
		textarea.value = textarea.value.substring(0,maxLen);
	}
	
	number = maxLen - textarea.value.length;
	
	if (number < 11) {
		count.innerHTML = number;
		count.style.color = "#e35351";
		count.style.fontWeight = "bold";
	} else {
		count.innerHTML = number;
		count.style.color = "#3d4e53";
		count.style.fontWeight = "normal";
	}
}