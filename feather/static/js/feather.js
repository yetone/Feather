function replyOne(username,number){
	replyContent = $("#editor-input");
	oldContent = replyContent.val();
	prefix = "#" + number + "楼" + " " + "@" + username + " ";
	newContent = '';
	if(oldContent.length > 0){
		if (oldContent != prefix) {
			newContent = oldContent + " " + prefix;
		}
	} else {
		newContent = prefix
	}
	replyContent.focus();
	if(number){
		replyContent.val(newContent);
	}
	moveEnd($("#editor-input"));
}


function thankReply(replyid){
	$.get('/reply/' + replyid + '/thank');
	if($('#thankcount-' + replyid).length){
		thankcount = Number($('#thankcount-' + replyid).html()) + 1;
		$('#thankcount-' + replyid).html(thankcount);
	} else {
		$('#thankview-' + replyid).html("<span id=\"heart\" class=\"list\" style=\"font-size: 11px; font-family: 'DejaVu Sans';\">♥</span><span class=\"thankcount\">1</span>")
	}
	$('#thank_area_' + replyid).addClass("thanked_area").removeClass("thank_area").html("♥");
}

function toReply(replyid){
	$('.isit').removeClass('isit');
	$('#' + replyid).parent('.left').parent('.clearbox').parent('article').parent('td').parent('tr').addClass('isit');
	id = parseInt(replyid) - 1;
	$.scrollTo('#' + id,500);
}

function fav(topicid){
	$.get('/topic/' + topicid + '/fav');
	$('show').html("已收藏");
	$('#fav').removeClass('btn btn_primary').addClass('btn disabled btn_primary');
}
