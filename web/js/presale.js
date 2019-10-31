$(function() {
	//语言切换
	$(".switchareaclick").click(function() {
		$(".switcharealist").fadeToggle()
	})
	
	var regular = /(en|En)/;
	var currenthref = window.location.href
	var current = regular.test(currenthref)
	var gurl = "http://47.52.224.216:8666/";

	/*获取剩余数量*/
	function surplus(){
		$.get(gurl + "get_presalenum", function(data) {
			var sellOutObj = JSON.parse(data)
			$(".sheng").each(function() {
				var start = $(this).siblings(".total").text();
				$(this).text(start)
			})
			//		console.log("剩余数量",sellOutObj)
			for(var i = 0; i <= sellOutObj.length - 1; i++) {
				var idType = sellOutObj[i].type
				var totalobj = $(".presalegame li").eq(idType - 1).find(".total").text()
				var shengReduce = $(".presalegame li").eq(idType - 1).find(".sheng").text(totalobj - sellOutObj[i].num)
				if(shengReduce.text() <= 0) {
					$(".presalegame li").eq(idType - 1).find(".sheng").text("0").css("color", "#f00")
					$(".presalegame li").eq(i).find(".game_price button").attr("disabled")
					$(".presalegame li").eq(i).find(".game_price button").removeClass("activetimebeginobj")
				}
			}
		})
	}
	surplus()
	/*获取开始时间*/
	$.get(gurl + "getSaleTm", function(data) {
		var time = JSON.parse(data);
		var timestamp = time.curTm
		setInterval(function() {
			timestamp = timestamp + 1000;
			var timebeginobj = time.begin;
			var timeendbj = time.end;
			var timeobjTimestamp;
			if(timebeginobj >= timestamp) {
				timeobjTimestamp = timebeginobj
			} else if(timeendbj > timestamp) {
				timeobjTimestamp = timeendbj
				$(".presale_time img").attr("src", "img/presaletime2.png")
				$(".presalegame li").each(function() {
					var currentindex = $(this).index()
					var indextext = $(this).find(".sheng").text()
					if(indextext > 0) {
						$(".presalegame li").eq(currentindex).find(".game_price button").removeAttr("disabled").addClass("activetimebeginobj")
					} else {
						$(".presalegame li").eq(currentindex).find(".game_price button").attr("disabled", "disabled").removeClass("activetimebeginobj")
					}
				})
			} else {
				$(".presale_time img").attr("src", "img/presaletime3.png")
				$(".presale_time div").css({
					"background": "url(img/presaletimebjend.png)",
					"text-shadow": "none"
				})
				$(".presalegame li").find(".game_price button").attr("disabled", "disabled")
				$(".presalegame li").find(".game_price button").removeClass("activetimebeginobj")
			}
			var surplusTime = (timeobjTimestamp - timestamp) / 1000
			var intDiff = parseInt(surplusTime); //倒计时总秒数量
			function timer(intDiff) {
				var day = 0,
					hour = 0,
					minute = 0,
					second = 0; //时间默认值    
				if(intDiff > 0) {
					day = Math.floor(intDiff / (60 * 60 * 24));
					hour = Math.floor(intDiff / (60 * 60)) - (day * 24);
					minute = Math.floor(intDiff / 60) - (day * 24 * 60) - (hour * 60);
					second = Math.floor(intDiff) - (day * 24 * 60 * 60) - (hour * 60 * 60) - (minute * 60);
				} else { //当时间耗尽，刷新页面
				}
				if(hour <= 9) hour = '0' + hour;
				if(minute <= 9) minute = '0' + minute;
				if(second <= 9) second = '0' + second;
				if(current) {
					$(".presale_time div").html('<font>' + day + "Day" + hour + ":" + minute + ':' + second + '</font>');
				} else {
					$(".presale_time div").html('<font>' + day + "天" + hour + ":" + minute + ':' + second + '</font>');
				}
			}
			timer(intDiff);
		}, 1000)
	})

	//获取登录状态
	var appid = "1000000";
	var appkey = "";
	var userInfo;
	var userbalance;
	var lang="cn";

	var listener = function(res) {
		//	            var resObj = document.getElementById('res')
		//	            resObj.innerHTML = '<pre>' + JSON.stringify(JSON.parse(data), null, 4) + '</pre>'

		console.log('listener, res =>', res);
		try {
			var resObj = JSON.parse(res)
			if(resObj.hasOwnProperty("cmd")) {
				switch(resObj.cmd) {
					case "changeNetTypeRes": // 网络切换回调
							balance()
							break;
					case "loginRes": // 登录回调
						userInfo = resObj.data;
						get_presale(resObj.data.wallet)
						loging()
						break;
					case "logoutRes": // 登出
						userInfo = null;
						clear_presale()
						break;
					case "getBalanceRes": // 获取余额
						userbalance = resObj.data.gas;
						break;
					case "getAppNotifysRes":
						for(let i in resObj.data) {
							let txid = resObj.data[i].txid;
							BlackCat.SDK.confirmAppNotify({
								txid: txid
							})
							let state = resObj.data[i].state;
							if(state=="1"){
								surplus()
								get_presale(userInfo.wallet)
							}
						}
						break;
				}
			}
		} catch(e) {
			console.log("eeeeeeeeeeeeeeeeeeeeeeeee", e)
		}
	};

	function balance(){
		BlackCat.SDK.getBalance()
	}
	function get_presale(wallet) {
		/*获取拥有数量*/
		var data = {
			address: wallet,
		}
		$.ajax({
			type: "get",
			url: gurl + "get_presale",
			dataType: 'json',
			data: data,
			success: function(data) {
				//					console.log("拥有",data)
				var preSaleList = $(".presalegame li").length
				for(var i = 0; i <= data.length - 1; i++) {
					var idType = data[i].type
					$(".presalegame li").eq(idType - 1).find(".game_price p label").text(data[i].num)
				}
				BlackCat.SDK.getBalance()
			}
		});
	}

	function clear_presale() {
		$(".game_price p label").text(0)
	}
	if(current){
		lang="en"
	}
	
	BlackCat.SDK.init(appid, appkey, listener,lang)
	BlackCat.SDK.login()
	//检测是否有登录
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

	/*点击交易*/
	$(".presalegame li").each(function() {

		var index = $(this).index()

		$(this).find(".game_price button").click(function() {

			console.log('userInfo', userInfo)
			if(!userInfo) {
				BlackCat.SDK.showMain()
				return;
			}

			var balance = $(this).find("label").text();
			if(Number(balance) > Number(userbalance)) {
				$(".insufficient").fadeIn()
				return;
			}

			var data = {
				toaddr: "Aakssdq6o3aL1PysQ23DEXrEeutwEeJeKQ",
				count: balance
			}

			var sellOuttypeid;
			$.get(gurl + "get_presalenum", function(json) {
				var sellOutObj = JSON.parse(json)

				var sellOutnum = {};
				sellOutObj.forEach(function(v) {
					if(v.type == index + 1) {
						sellOutnum = v;
					}
				});

				var sellOutNumber;
				if(sellOutnum.num != undefined) {
					sellOutNumber = sellOutnum.num + 1
				} else {
					sellOutNumber = 1
				}

				var totalobj = $(".presalegame li").eq(index).find(".total").text()
				var shengReduce = totalobj - sellOutNumber;
				if(sellOutNumber <= totalobj) {
					BlackCat.SDK.makeGasTransfer(data, function(res) {
						console.log("makeGasTransfer.callback.function.res ", res)
						if(res.err == false) {

							if(shengReduce <= 0) {
								$(".presalegame li").eq(index).find(".game_price button").attr("disabled")
								$(".presalegame li").eq(index).find(".game_price button").removeClass("activetimebeginobj")
								$(".presalegame li").eq(index).find(".game_attr .sheng").text(0).css("color", "#f00")
							}
							var purchaseinfo = {
								txid: "0x" + res.info,
								type: index + 1,
								address: userInfo.wallet,
							}

							$.ajax({
								type: "get",
								url: gurl + "presale",
								dataType: 'json',
								data: purchaseinfo,
								success: function(data) {
									console.log("购买情况", data)
									if(data.res == 1) {
//										$(".presalegame li").eq(index).find(".game_attr_role  .sheng").text(shengReduce)
//										var zong = $(".presalegame li").eq(index).find(".game_price p label").text()
//										zong++;
//										$(".presalegame li").eq(index).find(".game_price p label").text(zong)

										$(".purchaseSuccess").fadeIn()
									} else {
										$(".purchaseFail").fadeIn()
									}

								},
								error: function(data) {
									console.log("请求失败", data)
								}
							});

						}/* else {
							$(".purchaseFail").fadeIn()
						}*/
					})
				}
			})
		})
	})

	$(".sellout img").click(function() {
		$(this).parent().parent().fadeOut()
	})

})