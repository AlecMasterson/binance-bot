var express = require('express');
var router = express.Router();

router.get('/', function (req, res) {
    setTimeout(function () {
        var ran = Math.random();
        if (ran < 0.7) {
            res.send([
                {
                    name: "Alpha",
                    birth: "2019-11-20",
                    overall: 8.4,
                    weekly: 2.3,
                    trades: 9
                },
                {
                    name: "Beta",
                    birth: "2019-12-03",
                    overall: 5.7,
                    weekly: 1.2,
                    trades: 4
                },
                {
                    name: "Charlie",
                    birth: "2019-12-08",
                    overall: 2.7,
                    weekly: 2.2,
                    trades: 6
                }
            ]);
        } else if (ran < 0.87) {
            res.send([]);
        } else {
            res.status(500).send({ message: 'Test Error' });
        }
    }, 0500);
});

module.exports = router;