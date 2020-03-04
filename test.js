const fs = require("fs");

const CATEGORY = "ballet"

const files = fs.readdirSync("densepose/txt/" + CATEGORY);


var motion = [];
const FILE_NAME = "XwmwsGT8IQ4"

// console.log(files);
files.forEach(function(filename) {
	const parts = filename.split("_");
	if (parts[0] == FILE_NAME) {
		console.log(parts);
		var frame = Number(parts[parts.length-1].split(".")[0]);
		const data = fs.readFileSync("densepose/txt/" + CATEGORY + "/" +filename);
		motion[frame] = JSON.parse(data.toString());
	}
})


fs.writeFileSync(`frontend/src/data/${CATEGORY}_${FILE_NAME}_motion.json`, JSON.stringify(motion));
// _eqF-TA8TVQ_043_0001")