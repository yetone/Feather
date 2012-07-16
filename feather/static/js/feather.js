function replyOne(username){
	replyContent = $("#editor-input");
	oldContent = replyContent.val();
	prefix = "@" + username + " ";
	newContent = '';
	if(oldContent.length > 0){
		if (oldContent != prefix) {
			newContent = oldContent + prefix;
		}
	} else {
		newContent = prefix
	}
	replyContent.focus();
	replyContent.val(newContent);
	moveEnd($("#editor-input"));
}


function thankReply(replyid){
	$.get('/reply/' + replyid + '/thank');
	$('#thank_area_' + replyid).addClass("thanked_area").removeClass("thank_area").html("♥");
}


function fav(topicid){
	$.get('/topic/' + topicid + '/fav');
	$('show').html("已收藏");
	$('#fav').removeClass('btn btn_primary').addClass('btn disabled btn_primary');
}
