"use strict";
const id_GAS = "0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7";
const admin_wif = "L5kAoVhKtsGNntC9tenNLbAdY9zW5mRMQshHhiQDGSom3bv9N9F2";
const fishHash = "0x94a24ee381bc386daa91984c7dd606f6fdd8f19e";
const admin_refund_address = "ATXKGbfP7pvonXkoCzE1MySJuLZrUokT9E";
//内部cli调用端口
const api = "https://api.nel.group/api/testnet";

Object.defineProperty(exports, "__esModule", { value: true });
var fs = require("fs");
var readline = require("readline");
loadNormalJSs("neo-ts.js", ["Neo", "ThinNeo"]);
loadNormalJSs("scrypt-async.js", ["scrypt"]);
var db = require("./db.js");

var jsname = ""

async function init(name)
{
	jsname = name;
	await db.init(name);
}

//习惯了直接加载，require 只支持commonjs 不方便
function loadNormalJS(filename, namespace) {
    var js = fs.readFileSync(__dirname + "/" + filename).toString();
    //我这样加一句把命名空间丢进global，对nodejs来说，就可以访问了
    //global["fuck"] =fuck; 相当于在js文件后面加上这样一句
    js += "\r\n global['" + namespace + "']=" + namespace;
    eval(js);
}

function loadNormalJSs(filename, namespaces) {
    var js = fs.readFileSync(__dirname + "/" + filename).toString();
    for (var i = 0; i < namespaces.length; i++) {
        js += "\r\n global['" + namespaces[i] + "']=" + namespaces[i];
    }
    eval(js);
}

function addr2hash(addr)
{
    var retVal = ThinNeo.Helper.GetPublicKeyScriptHash_FromAddress(addr);
	retVal = retVal.toHexString()
    return retVal;
} 

function addr2hash_r(addr)
{
    var retVal = ThinNeo.Helper.GetPublicKeyScriptHash_FromAddress(addr);
	retVal = retVal.reverse().toHexString()
    return retVal;
} 

function hash2addr(hash)
{
	var bs = hash.hexToBytes();
	return ThinNeo.Helper.GetAddressFromScriptHash(bs);
}

function r_hash2addr(hash)
{
	var bs = hash.hexToBytes().reverse();
	return ThinNeo.Helper.GetAddressFromScriptHash(bs);
}

function hash2string(hash)
{
    var bs = hash.hexToBytes();
    var retVal2 = ThinNeo.Helper.Bytes2String(bs)
    return retVal2;
} 

function hash2int(hash)
{
    var bytes = hash.hexToBytes();
    var retval = new Neo.BigInteger(bytes).toString();
    return retval;
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

function makeRpcPostBody(method, scripthash)
{
    var params = [];
    params.push(scripthash);
    return makeRpcPostBodyT(method, params)
}

function makeRpcPostBodyT(method, params)
{
    var body = {};
    body["jsonrpc"] = "2.0";
    body["method"] = method;
    body["params"] = params;
    body["id"] = 1;
    return body;
}

function get_wifkey(path, password)
{
    var wallet = new ThinNeo.nep6wallet();
    var data = fs.readFileSync(path,'utf-8');
    wallet.fromJsonStr(data);
    var account = wallet.accounts[0];
    account.getPrivateKey(wallet.scrypt, password, (info, result) =>{
        var wifkey = ThinNeo.Helper.GetWifFromPrivateKey(result);
        console.log(wifkey);
    });
}

function makeTran(sb)
{
	var admin_prikey = ThinNeo.Helper.GetPrivateKeyFromWIF(admin_wif);
	var admin_pubkey = ThinNeo.Helper.GetPublicKeyFromPrivateKey(admin_prikey);
	var admin_address = ThinNeo.Helper.GetAddressFromPublicKey(admin_pubkey);
	var admin_addressHash = ThinNeo.Helper.GetPublicKeyScriptHash_FromAddress(admin_address);
	
    var tran = new ThinNeo.Transaction();
	tran.version = 0;
    tran.type = ThinNeo.TransactionType.InvocationTransaction;
    tran.extdata = new ThinNeo.InvokeTransData();
	tran.extdata.script = sb.ToArray();
    tran.inputs = [];
	tran.outputs = [];
	tran.attributes = [];
	tran.attributes[0] = new ThinNeo.Attribute();
	tran.attributes[0].usage = ThinNeo.TransactionAttributeUsage.Script;
	tran.attributes[0].data = admin_addressHash;
    var msg = tran.GetMessage();
    var signdata = ThinNeo.Helper.Sign(msg, admin_prikey);
    tran.AddWitness(signdata, admin_pubkey, admin_address);
    let txid = tran.GetHash().clone().reverse().toHexString();
	return tran;
}

function addTranOrder(sb, callback)
{
	db.get_operation(jsname).then(result => {
		console.log("Order: " + result);
		var n = new Neo.BigInteger(result);
		sb.EmitPushString(jsname);
		sb.Emit(ThinNeo.OpCode.DROP);
		sb.EmitPushNumber(n);
		sb.Emit(ThinNeo.OpCode.DROP);
		callback(sb);			
	});	
}

function sendRpc(data, method, callback)
{
	var datahash = data.toHexString();
	var postdata = makeRpcPostBody(method, datahash);
	var request = require('request');
	request.post({
		url:api,
		body:postdata,
		json:true
	}, callback
	);
}

///////////////////////////////////////////////////////////////////////

function deploy()
{    
    var scriptaddress = fishHash.hexToBytes().reverse();
    var ysb = new ThinNeo.ScriptBuilder();
	addTranOrder(ysb, sb => {
		sb.EmitParamJson(["([])"]);
		sb.EmitPushString("deploy");
		sb.EmitAppCall(scriptaddress);
		var tran = makeTran(sb)
		var data = tran.GetRawData();
		sendRpc(data, "sendrawtransaction", function (error, response, body) {
			if (!error && response.statusCode == 200) {
				console.log(body);
			} else {
				console.log(error, body);
			}
		});
	});
}

function total_mine()
{
	var scriptaddress = fishHash.hexToBytes().reverse();
    var sb = new ThinNeo.ScriptBuilder();
	sb.EmitParamJson(["([])"]);
    sb.EmitPushString("totalMine");
    sb.EmitAppCall(scriptaddress);
    var data = sb.ToArray();
	sendRpc(data, "invokescript", function (error, response, body) {
		if (!error && response.statusCode == 200) {
			var v = body.result[0].stack[0].value
			var r = hash2int(v);
			console.log(r);
        }
	});
}

function mine()
{
	var scriptaddress = fishHash.hexToBytes().reverse();
    var ysb = new ThinNeo.ScriptBuilder();
	addTranOrder(ysb, sb => {
		sb.EmitParamJson(["([])"]);
		sb.EmitPushString("mine");
		sb.EmitAppCall(scriptaddress);
		var tran = makeTran(sb)
		var data = tran.GetRawData();
		sendRpc(data, "sendrawtransaction", function (error, response, body) {
			if (!error && response.statusCode == 200) {
				console.log(body);
			} else {
				console.log(error, body);
			}
		});
	});
}

function refund(_id, who, num)
{
	if (who == '')
	{
		who = admin_refund_address;
	}
	var scriptaddress = fishHash.hexToBytes().reverse();
    var ysb = new ThinNeo.ScriptBuilder();
	addTranOrder(ysb, sb => {
		sb.EmitParamJson(["(addr)" + who, "(int)" + num]);
		sb.EmitPushString("refund");
		sb.EmitAppCall(scriptaddress);
		var tran = makeTran(sb)
		var data = tran.GetRawData();
		sendRpc(data, "sendrawtransaction", function (error, response, body) {
			if (!error && response.statusCode == 200) {
				console.log(body);
				if (body.result.length > 0)
				{
					var txid = body.result[0].txid;
					db.confirm_refund(_id, txid);					
				}
			} else {
				console.log(error, body);
			}
		});
	});
}

async function refund_loop()
{
	var rf = await db.get_unconfirm_refund();
	if (rf != null)
	{
		refund(rf["_id"], rf["who"], rf["num"]);
	}
}

function tx_info(txid)
{
	var scriptaddress = fishHash.hexToBytes().reverse();
    var sb = new ThinNeo.ScriptBuilder();
	sb.EmitParamJson(["(hex256)" + txid]);
    sb.EmitPushString("getTxInfo");
    sb.EmitAppCall(scriptaddress);
    var data = sb.ToArray();
	sendRpc(data, "invokescript", function (error, response, body) {
		if (!error && response.statusCode == 200) {
			var v = body.result[0].stack[0].value
			console.log(v);
        }
	});
}

function balance_of(addr)
{
	var scriptaddress = fishHash.hexToBytes().reverse();
    var sb = new ThinNeo.ScriptBuilder();
	sb.EmitParamJson(["(addr)" + addr]);
    sb.EmitPushString("balanceOf");
    sb.EmitAppCall(scriptaddress);
    var data = sb.ToArray();
	sendRpc(data, "invokescript", function (error, response, body) {
		if (!error && response.statusCode == 200) {
			var v = body.result[0].stack[0].value
			var r = hash2int(v);
			console.log(r);
        }
	});
}

function transfer(from, to, num)
{
	var scriptaddress = fishHash.hexToBytes().reverse();
    var ysb = new ThinNeo.ScriptBuilder();
	addTranOrder(ysb, sb => {
		sb.EmitParamJson(["(addr)" + from, "(addr)" + to, "(int)" + num]);
		sb.EmitPushString("transfer");
		sb.EmitAppCall(scriptaddress);
		var tran = makeTran(sb)
		var data = tran.GetRawData();
		sendRpc(data, "sendrawtransaction", function (error, response, body) {
			if (!error && response.statusCode == 200) {
				console.log(body);
			} else {
				console.log(error, body);
			}
		});
	});
}

module.exports = {
	init,
	
	addr2hash,
	addr2hash_r,
	hash2addr,
	r_hash2addr,

    deploy,
	total_mine,
	mine,
	refund_loop,
	tx_info,
	balance_of,
	transfer,
}