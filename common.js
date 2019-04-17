var userPath="http://localhost:8000/"
var chatPath="ws://localhost:9000/"
$(document).ready(function() {
	initial();
	if (window.location.href.indexOf("login")!=-1){
		//啥也不做
	}else{
		if(sessionStorage.getItem("username")==null&&window.location.href!=userPath+"login/"){
		alert("很抱歉，未登录用户不能使用，正在为您跳转至登录页面...");
		window.location.href=userPath+"login/";
	}
	}
});
function initial(){
	/**
	* 解决mui中a标签的href属性无法跳转问题
	* 
	*/
	$("a").on("tap",function(){
		if(this.name){
			window.location.href=userPath+this.name;
		}else if(this.href){
			window.location.href=this.href;
		}
	});
	/**
	 * 增加自滚动功能
	 */
	mui('.self-scroll').scroll();
}
/**
 * 时间戳转换
 */
function getLocalTime(timer){
	console.log(new Date(parseInt(timer) * 1000).toLocaleString().replace(/:\d{1,2}$/,' '));
	return new Date(parseInt(timer) * 1000).toLocaleString().replace(/:\d{1,2}$/,' ');
}
function getHMtime(){
	
}
/*
聊天连接
 */
var socket;
function connect() {
	var host = chatPath
	socket = new WebSocket(host);
	try {
		socket.onopen = function (msg) {
			var list={'userid':sessionStorage.getItem('id'),"type":"test",'content':0,"to":"0","ctime":new Date().getTime()};
			socket.send(JSON.stringify(list));
			$("btnConnect").disabled = true;
                  console.log("连接聊天服务成功！");
                };
		socket.onclose = function (msg) {
			var list={'userid':sessionStorage.getItem('id'),"type":"state",'content':"closed","to":"0","ctime":new Date().getTime()};
			socket.send(JSON.stringify(list));
			$("btnConnect").disabled = true;
				alert("聊天服务已断开，正在为您重连...") };
            }
            catch (ex) {
                log(ex);
            }
        }