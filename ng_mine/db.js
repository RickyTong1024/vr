var mongodb = require('mongodb')
const MongoClient = mongodb.MongoClient
const DB_URL = 'mongodb://localhost:27017'

var jsdb = null;
var op = 0;
var op_max = 0;
const op_step = 100;

async function init(name)
{
	var mdb = await MongoClient.connect(DB_URL, { useNewUrlParser: true });
	jsdb = mdb.db("jsdb");
	await jsdb.createCollection("operation_" + name);
	await jsdb.createCollection("refund_num");
	await jsdb.createCollection("refund");
	await jsdb.collection("refund").createIndex({"id" : 1});
	await jsdb.collection("refund").createIndex({"comfirm" : 1});
}

async function get_operation(type)
{
	if (op < op_max)
	{
		op = op + 1;
		return op;
	}
	else
	{
		op = await jsdb.collection("operation_" + type).findOne();
		if (op == null)
		{
			await jsdb.collection("operation_" + type).insertOne({"op" : op_step});
			op = 0;
			op_max = op_step;
		}
		else
		{
			await jsdb.collection("operation_" + type).updateOne({}, {$set:{"op" : op["op"] + op_step}});
			op = op["op"];
			op_max = op + op_step;
		}
	}
	return op;
}

async function get_unconfirm_refund()
{
	var now = Math.floor(new Date().getTime() / 1000)
	var t = now - 30;
	refund = await jsdb.collection("refund").findOne({"confirm" : 0, "last_time" : {$lte : t}});
	if (refund != null)
	{
		await jsdb.collection("refund").updateOne({"_id" : refund["_id"]}, {$set:{"last_time" : now}});
	}
	return refund;
}

async function confirm_refund(_id, tran)
{
	await jsdb.collection("refund").updateOne({"_id" : _id}, {$set:{"confirm" : 1, "transaction" : tran}});
}

module.exports = {
	init,
	get_operation,
	get_unconfirm_refund,
	confirm_refund,
}
