const fs = require("fs");
const path = require("path");

BASE_DIR = path.join(__dirname, "../densepose/txt/")

const dirs = fs.readdirSync(BASE_DIR);

const fileListing = {};

const FRAME_DESCRIPTOR_LENGTH = "_1234.json".length;

dirs.forEach(category => {
	fileListing[category] = {};
	const files = fs.readdirSync(path.join(BASE_DIR, category));
	files.forEach(file => {
		const fileId = file.substring(0, file.length - FRAME_DESCRIPTOR_LENGTH);
		const parts = file.split("_");
		const frame = Number(parts[parts.length-1].split(".")[0]);
		fileListing[category][fileId] = fileListing[category][fileId] || [1, -1]
		// The 2nd element in the array will be the last frame 
		fileListing[category][fileId][1] = frame;
	})
})

fs.writeFileSync(path.join(__dirname, "dancetxtdirectory.json"), JSON.stringify(fileListing));