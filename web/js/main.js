var regular = /(en|En)/;
var currenthref = window.location.href
current = regular.test(currenthref)

//黑猫登录情况
var appid = "1000000";
var appkey = "";
var userInfo;
var lang = "cn"
if(current) {
	lang = "en"
}
var listener = function(res) {
	try {
		var resObj = JSON.parse(res)
		if(resObj.hasOwnProperty("cmd")) {
			switch(resObj.cmd) {
				case "loginRes": // 登录回调
					userInfo = resObj.data;
					loging()
					break;
			}
		}
	} catch(e) {
		console.log("eeeeeeeeeeeeeeeeeeeeeeeee", e)
	}
};

BlackCat.SDK.init(appid, appkey, listener, lang)
BlackCat.SDK.login()

$(".pc_icon").hide()

function loging() {
	$(".loging a").hide()
	$(".pc_icon").show().addClass("show")
}
$(".loging a").click(function() {
	$(this).fadeOut()
	BlackCat.SDK.showMain()
	$(".pc_icon").fadeIn().addClass("show")
})



$(function() {

	/*导航栏*/
	$(".nav_ul li").click(function() {
		$(".nav_ul li").removeClass("active");
		$(this).addClass("active");
	});
	$(".nav_ul a,.switcharealist a").click(function() {
		if($(this).attr("href") == "#") {
			if(current) {
				alert('Coming soon!');
			} else {
				alert('敬请期待!');
			}

		}
	});
	$(".switchareaclick").click(function() {
		$(".switcharealist").fadeToggle()
	})

	//公告打开新窗口
	$(".gxgg li a").attr("target", "_blank")

})