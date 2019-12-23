var express = require('express');
var router = express.Router();

var mysql = require('mysql');
var connection = mysql.createConnection({
	host: 'binance-bot.cfypif4yfq4f.us-east-1.rds.amazonaws.com',
	user: 'epsenex',
	password: 'Minecraft#1PUBG#2',
	database: 'test2'
});
connection.connect();

router.get('/get-balances', function(req, res, next) {
	connection.query('SELECT * FROM BALANCES', function(err, rows, fields) {
		if (err) throw err
		res.json(rows)
	});
});

router.get('/get-policies', function(req, res, next) {
	connection.query('SELECT * FROM POLICIES', function(err, rows, fields) {
		if (err) throw err
		res.json(rows)
	});
});

router.get('/get-history/:coinpair', function(req, res, next) {
	connection.query('SELECT * FROM ' + req.params['coinpair'], function(err, rows, fields) {
		if (err) throw err
		res.json(rows)
	});
});

module.exports = router;
