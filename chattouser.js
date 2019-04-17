$(document).ready(function () {
    /**
     * 布局初始化
     */
    var clientHeight = document.body.clientHeight;
	var inputWrapHeight = $("#input-wrap").outerHeight();
	var titleHeight = $(".mui-title").outerHeight();
	$("#content").height(clientHeight - inputWrapHeight);
	$(".mui-content").css("margin-top", titleHeight);
	$(".mui-content").height(clientHeight - inputWrapHeight - titleHeight);
	$(".mui-content").css('minHeight',clientHeight - inputWrapHeight - titleHeight);
	mui('#pullrefresh').scroll({
		deceleration: 0.0005,//flick 减速系数，系数越大，滚动速度越慢，滚动距离越小，默认值0.0006
		indicators:false
	});
    /**
     * 初始化聊天数据
     * 1.从本地获取聊天数据
     * 2.从网络加载聊天数据
     * 聊天
     * 1.登录时即连接到聊天系统
     */
    connect();
    var str = window.location.href;
    touserid = str.split('/chattouser/')[1].split("/")[0];
    $("h1").text(sessionStorage.getItem("username"+touserid));
    $("#sendtouser").focus();
    $("#sendtouser").keypress(function (e) {
        if (e.keyCode === 13) {  // enter, return
            var messageInputDom = document.querySelector('#sendtouser');
            var message = messageInputDom.value;
            var ctime=new Date().getTime();
            var list = {
                'userid': sessionStorage.getItem('id'),
                "type": "text",
                'content': message,
                "to": touserid,
                "ctime": ctime
            };
            socket.send(JSON.stringify(list));
            messageInputDom.value = '';
            socket.onmessage = function (msg) {
			var resstr=msg.data;
			resstr=JSON.parse(resstr);
			console.log(resstr)
			var content=resstr['msg'][0]['content'];
			var fromuserid=resstr['msg'][0]['fromuserid'];
			var type=resstr['msg'][0]['type'];
			console.log(content);
			if(fromuserid==touserid){
			    if(type=='text'){
			        var li = "<li class='content-left'>" +
                        "<img src='"+userPath+"static/userheadpic/"+sessionStorage.getItem("headpicurl"+touserid)+"' />" +
                        "<a>" + getLocalTime(parseInt(new Date().getTime()) / 1000) + "</a>" +
                        "<span>" + content + "</span>" +
                        "</li>";
                    $(".ul-content").append(li);
                }
                mui('#pullrefresh').scroll().refresh();
                mui('#pullrefresh').scroll().scrollToBottom(100);
            }else if(fromuserid=='0'){//todo
			        if(type=='state'){
			        var li = "<li class='content-right'>" +
                        "<img src='"+userPath+sessionStorage.getItem("headpicurl")+"' />" +
                        "<a>" + getLocalTime(parseInt(new Date().getTime()) / 1000) + "</a>" +
                        "<span>" + content + "</span>" +
                        "</li>";
                    $(".ul-content").append(li);
                }
                mui('#pullrefresh').scroll().refresh();
                mui('#pullrefresh').scroll().scrollToBottom(100);
                    }
                };
        }
    })
})
