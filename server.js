const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = process.env.PORT || 8080;

const processFramesForDance = require("./preprocess/process-frames");

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));


async function randomDance(category) {
	const danceIndex = require("./preprocess/dancetxtdirectory.json");
	if (!category) {
		const categories = Object.keys(danceIndex);
		category = categories[Math.floor(Math.random() * categories.length)];
	}

	const dances = danceIndex[category];

	if (!dances) {
		return { err: "Invalid category" };
	}

	const ids = Object.keys(dances);
	const id = ids[Math.floor(Math.random() * ids.length)];
	return await processFramesForDance({id: id, category: category});
}

app.get('/api/dance/random', async (req, res) => {
	res.send(await randomDance());
});

app.get('/api/dance/:category/random', async (req, res) => {
	res.send(await randomDance(req.params.category));
});

app.get('/api/dance/:category/:id', async (req, res) => {
	console.log(req.params.id);
	res.send(await processFramesForDance({id: req.params.id, category: req.params.category}));
});

app.listen(port, () => console.log(`Listening on port ${port}`));