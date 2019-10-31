"use strict";

const http = require('http');
//const host = "127.0.0.1";
const post = "8666";
const url = require('url');
const queryString = require('querystring');
const query = require("./mysql_pool.js");
const addr = "Aakssdq6o3aL1PysQ23DEXrEeutwEeJeKQ";
let txidlist = []; 

var type_conf = [
	{"type":1,"price":14.99,"num":5},
	{"type":2,"price":14.99,"num":30},
	{"type":3,"price":14.99,"num":700},
	{"type":4,"price":14.99,"num":1400},
	{"type":5,"price":4.99,"num":1400},
	{"type":6,"price":4.99,"num":2000},
	{"type":7,"price":4.99,"num":4000},
];

var begin_date = "2019-01-1 13:00:00";
var end_date = "2019-02-30 23:59:59"; 
var beginDate = new Date(begin_date);
var beginTm = beginDate.getTime();
var endDate = new Date(end_date);
var endTm = endDate.getTime();


var server = http.createServer(function(req,res){
	res.setHeader('Access-Control-Allow-Origin','*');
	
	let methods = req.method;
	let onRes = {"res":1};
	if(methods == "GET")
	{
		let params = url.parse(req.url,true,true);
		//console.log(params);
		switch(params.pathname)
		{
			case "/presale":
			{
				// console.log(params);
				var curTm = Date.now();
				// console.log(beginTm,endTm,curTm);
				if(curTm < beginTm || curTm > endTm)
				{
					// console.log(params.query.txid+"timeoff");
					onRes.res = -3;
					res.setHeader("content-type","text/html;charset=UTF-8");
					res.end(JSON.stringify(onRes));
					break;
				}

				var select_sql = "select * from presale where txid=? and address=?";
				query(select_sql,[params.query.txid,params.query.address],function(err,results,fields){
					// console.log(err,results);
					if(!err && results.length == 0)
					{
						if (typeof(params.query.txid) == "string" && params.query.txid.length == 66)
						{
							var insert_sql = "insert into presale(txid,type,address,tm) values(?,?,?,?)";
							var insert_options = [params.query.txid,params.query.type,params.query.address,Date.now()/1000];
							query(insert_sql,insert_options,function(err,results,fields){
								// console.log(results);
								if(!err){
									txidlist.push({"txid":params.query.txid,"type":params.query.type,"address":params.query.address});
								}else{	
									console.error("insert mysql error:"+err);
								}
							})
						}else{
							onRes.res = -2;
						}					
					}else if(results.length > 0){
						onRes.res=-1;
					}
					res.setHeader("content-type","text/html;charset=UTF-8");
					res.end(JSON.stringify(onRes));
				});
				break;
			}
			case "/get_presale":
			{
				// var get_presale_sql = "select * from presale where address=?";
				var get_presale_sql = "select type,count(1) as num from presale where state=1 and address=? and tm>? and tm<? group by type";
				query(get_presale_sql,[params.query.address,beginTm/1000,endTm/1000],function(err,results,fields){
					if(!err)
					{
						res.setHeader("content-type","text/html;charset=UTF-8");
						res.end(JSON.stringify(results));
					}
				})
				break;
			}
			case "/get_presalenum":
			{
				var get_presale_sql = "select type,count(1) as num from presale where state=1 and tm>? and tm<? group by type";
				query(get_presale_sql,[beginTm/1000,endTm/1000],function(err,results,fields){
					if(!err)
					{
						res.setHeader("content-type","text/html;charset=UTF-8");
						res.end(JSON.stringify(results));
					}
				})
				break;
			}
			case "/get_officialaddr":
			{
				res.end(addr);
				break;
			}
			case "/getSaleTm":
			{
				res.end(JSON.stringify({"begin":beginTm,"end":endTm,"curTm":Date.now()}));
				break;
			}
			case "/getconf":
			{
				res.end(JSON.stringify(type_conf));
				break;
			}
		}
	}else{
		let datas = "";
		req.on("data",(chunk)=>{
			datas += chunk;
			// console.log(datas);
		})


		req.on("end",()=>{
			let postData = queryString.parse(datas.toString());
			// console.log(postData);

			res.setHeader("content-type","text/html;charset=UTF-8");
			res.end(addr);
		})
		
	}
}).listen(post,()=>{
	console.log("server is ready on port 8666");
});



//定时任务
const schedule = require('node-schedule');
var rule = new schedule.RecurrenceRule();
var times = [];
for(var i=0;i<60;)
{
	times.push(i);
	i+=4;
}

rule.second = times;

schedule.scheduleJob(rule,checktxid);

const api = "https://api.nel.group/api/mainnet"
const fetch = require('node-fetch');



//	-1 不是utxo转账  -2 收款不对 -3 没有这个类型  -4 转账金额不足  -5 付款方不对
//
//
//
async function checktxid()
{
	for(var i=0;i<txidlist.length;i++)
	{
		var txid = txidlist[i].txid;
		var type = txidlist[i].type;
        var json = await gettxinfo(txid);
        var state = 0;
        if(json.error)
        {
        	continue;
        }else{
        	if(json.result[0].vout.length > 0)
        	{

        		var vin_txid = json.result[0].vin[0].txid;
        		var vin_key = json.result[0].vin[0].vout;

        		var vin_json = await gettxinfo(vin_txid);
        		var from = vin_json.result[0].vout[vin_key].address;

        		if(json.result[0].vout[0].address == from)
        		{
        			state = -1;
        		}else{
        			var to = json.result[0].vout[0].address;
        			var value = json.result[0].vout[0].value;
        		}
	        	if(to == addr)
	        	{
	        		var state = 0;
	        		var price = get_price_by_type(type);
	        		if(price < 0)
	        			state = -3;
	        		else if(value < price)
	        			state = -4;
	        		else
	        			state = 1;

	        		if(from != txidlist[i].address)
	        			state = -5;
	        		
	        	}else{
	        		state = -2;
	        	}
        	}else{
        		state = -1;
        	}
			var options = [state,txidlist[i].txid];
			console.log(options);
			var update_sql = "update presale set state=? where txid=?";
			query(update_sql,options,function(err,results,fields){
				// console.log(results);
				if(err)
					console.error("insert mysql error:"+err);
			})
        	txidlist.splice(i,1);
        	// console.log(txidlist);
        	--i;
        }
	}
}

function get_price_by_type(type)
{
	for(var i=0;i< type_conf.length;i++)
	{
		if(type == type_conf[i].type)
			return type_conf[i].price;
	}
	return -1;
}

function gettxinfo(txid)
{
	var str = makeRpcUrl(api,"getrawtransaction",txid,1);
	// console.log(str);
	var result = fetch(str, { "method": "get" }).then(function (resp) {
    	return resp.json();
    });
    return result;
}

function makeRpcUrl(url, method) {
    var _params = [];
    for (var _i = 2; _i < arguments.length; _i++) {
        _params[_i - 2] = arguments[_i];
    }
    if (url[url.length - 1] != '/')
        url = url + "/";
    var urlout = url + "?jsonrpc=2.0&id=1&method=" + method + "&params=[";
    for (var i = 0; i < _params.length; i++) {
        urlout += JSON.stringify(_params[i]);
        if (i != _params.length - 1)
            urlout += ",";
    }
    urlout += "]";
    return urlout;
}