var express = require('express');
var router = express.Router();

router.get('/symbols', function (req, res, next) {
    const query = "SELECT DISTINCT symbol FROM history";

    db.query(query, (error, results) => {
        if (error) res.status(500).send(error);

        symbols = [];
        results.forEach(item => {
            symbols.push(item.symbol);
        });

        res.send(symbols);
    });
});

router.post('/decision', function (req, res) {
    let query = "SELECT * FROM decision";

    if (Object.keys(req.query).length != 0) query += " WHERE ";

    let multiple = false;
    if (req.query.hasOwnProperty("symbol")) {
        query += "symbol='" + req.query.symbol + "'";
        multiple = true;
    }

    if (req.query.hasOwnProperty("closeTime")) {
        if (multiple) query += " AND ";
        query += "close_time='" + req.query.closeTime + "'";
    }

    db.query(query, (error, data) => {
        if (error) res.status(500).send(error);
        res.send(data);
    });
});

router.post('/position', function (req, res) {
    res.send([]);
});

module.exports = router;