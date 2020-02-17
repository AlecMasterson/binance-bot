const router = require('express').Router();
const History = require('../services/History');

router.get('/test', function (req, res) {
    res.send('Hello from the Binance Bot!');
});

router.post('/history/count', async function (req, res) {
    const count = await History.getCount(req.query.symbol);
    res.send(`Count: ${count}`);
});

module.exports = router;