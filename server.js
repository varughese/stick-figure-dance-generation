const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = process.env.PORT || 8080;

const processFramesForDance = require("./preprocess/process-frames");

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.get('/api/dance/:category/:id', async (req, res) => {
	console.log(req.params.id);
	res.send(await processFramesForDance({id: req.params.id, category: req.params.category}));
});

app.listen(port, () => console.log(`Listening on port ${port}`));