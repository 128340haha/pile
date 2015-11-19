//导航js
$(document).ready(function($) {
	$('<div id="navphone"></div>').html($('#navlist').html() ).prependTo($('body'))

	$('#navbtn').click(function(){
		if($('#navbtn').hasClass('open'))
		{
			$('body').css('overflow','auto');
			$('#navphone').removeClass('open');
			$('#navbtn').removeClass('open')
		}
		else
		{
			$('body').css('overflow','hidden');
			$('#navphone').addClass('open');
			$('#navbtn').addClass('open')
		}
 			
	})
})
 
$(window).scroll(function(){
	if($(window).scrollTop()>0 && $(window).width()>768)
	{
		 $('#navbar').addClass('move');
	}
	else
	{
		 $('#navbar').removeClass('move');
	}
}) 
 
$(document).ready(function () {
  $('#weixin').popover({
	placement:'top',
	trigger:'click',
	html:true,
	content:'<div style="width:150px; height:150px;"><img src="images/wechat.jpg" class="img-responsive"/> </div>' 
  })
}) 
