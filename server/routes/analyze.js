var express = require('express');
var router = express.Router();

router.get('/symbols', function (req, res) {
    res.send(['BNBBTC', 'ETHBTC', 'DOGEBTC']);
});

router.get('/intervals', function (req, res) {
    if (req.query.symbol == 'BNBBTC') res.send(['4h', '6h']);
    if (req.query.symbol == 'ETHBTC') res.send(['2h', '6h']);
    res.send([]);
});

router.get('/data', function (req, res) {
    setTimeout(function () {
        res.send([]);
    }, 1500);
});

module.exports = router;