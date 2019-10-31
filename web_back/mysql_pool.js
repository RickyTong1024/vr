var mysql = require('mysql');
var pool = mysql.createPool({
	host:'localhost',
	user:'root',
	password:'root',
	database:'presale',
	port:3306
});

var query = function(sql,options,callback)
{
	pool.getConnection(function(err,conn){
		if(err){
			callback(err,null,null);
		}else{
			conn.query(sql,options,function(err,results,fields){
				conn.release();
				callback(err,results,fields);
			})
		}
	});
}

module.exports=query;