const router = require('express').Router();

router.get('/test', function (req, res) {
    res.send('Hello from the Binance Bot!');
});

module.exports = router;