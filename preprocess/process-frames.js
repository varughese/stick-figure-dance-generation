const fs = require("promise-fs");
const path = require("path");
const index = require("./dancetxtdirectory.json");

const FRAME_LENGTH = 4; // The filenames have 4 spots in them

function toFileName(id, frame) {
	const frameStr = frame + "";
	const zeros = "0".repeat(FRAME_LENGTH - frameStr.length);
	return id + "_" + zeros + frame + ".json";
}


/* USAGE:
	framesToArray({id: "_FidGI7J718_039", category: "swing" })
		.then(motion => console.log(motion))
*/

async function framesToArray({ id, category}) {
	var motion = [];
	const frameRange = index[category] ? index[category][id] : false;
	if (!frameRange) return { err: `${category}/${id} not found in index` };

	const [minframe, maxframe] = frameRange;
	
	for(let frame=minframe; frame<maxframe; frame++) {
		try {
			const file = await fs.readFile(path.join(__dirname, "../densepose/txt/", category, toFileName(id, frame)));
			// We do frame-1 because the dataset starts frames at 1
			motion[frame-1] = JSON.parse(file.toString());
		} catch (e) {
			return { err: e };
		}
	}

	if (motion.length === 0) {
		return { err: `${category}/${id} not found` };
	} else {
		return { id, category, motion };
	}
}

module.exports = framesToArray;