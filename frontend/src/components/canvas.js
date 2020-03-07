import React, { Component } from "react";
const ReactAnimationFrame = require('react-animation-frame');
// const data = require("../data/yimGp0XUcEE_motion.json");
const data = require("../data/y6kboFhoxow_motion.json");


// this is janky code

const bodyPartToIndexMap = {
	"nose": 1,
	"left_eye": 2,
	"right_eye": 3,
	"left_ear": 4,
	"right_ear": 5,
	"left_shoulder": 6,
	"right_shoulder": 7,
	"left_elbow": 8,
	"right_elbow": 9,
	"left_wrist": 10,
	"right_wrist": 11,
	"left_hip": 12,
	"right_hip": 13,
	"left_knee": 14,
	"right_knee": 15,
	"left_ankle": 16,
	"right_ankle": 17
}

class CanvasBase extends Component {
	constructor(props) {
		super(props);
		this.state = { frame: 0 };
		this.frame = 0;
	}

	componentDidMount() {
		const canvas = this.refs.canvas
		this.ctx = canvas.getContext("2d");
		this.ctx.lineWidth = 10;
	}

	drawCurrentFrame() {
		const { frame } = this;
		const frameData = data[frame];
		if (!frameData) return;
		this.ctx.clearRect(0, 0, 2000, 1000);
		const NUM_PEOPLE_TO_DRAW = frameData.length;
		for(let person=0; person < NUM_PEOPLE_TO_DRAW; person++) {
			this.drawPerson(frameData[person]);
			// There are multiple people per frame
		}
	  }
	
	drawPerson(coords) {
		// Draw Head
		const left_ear_coords = coords[bodyPartToIndexMap.left_ear][1];
		const right_ear_coords = coords[bodyPartToIndexMap.right_ear][1];
		let headCenterX = (left_ear_coords[0] + right_ear_coords[0])/2;
		let headCenterY = (left_ear_coords[1] + right_ear_coords[1])/2
		const headRadius = 40;
		this.ctx.beginPath();
		this.ctx.arc(headCenterX, headCenterY, headRadius, 0, 2 * Math.PI, false);
		this.ctx.fill();

		// TODO - there are probably more visually appealing ways to draw this
		const paths = [
			["left_shoulder", "left_elbow", "left_wrist"],
			["right_shoulder", "right_elbow", "right_wrist"],
			["right_hip", "right_knee", "right_ankle"],
			["left_hip", "left_knee", "left_ankle"],
			["left_shoulder", "right_shoulder", "right_hip", "left_hip", "left_shoulder"],
		];

		paths.forEach((path) => {
			this.ctx.beginPath();
			let [x, y] = coords[bodyPartToIndexMap[path[0]]][1];
			this.ctx.moveTo(x, y)
			for(let i=1; i<path.length; i++) {
				const bodyPart = path[i];
				[x, y] = coords[bodyPartToIndexMap[bodyPart]][1];
				this.ctx.lineTo(x, y);
			}
			this.ctx.stroke();
		})
	}



	onAnimationFrame(time) {
		if (this.frame === data.length) {
			// TODO - pass in data to the component as a prop instead of hard coding it lol
			this.props.endAnimation();
			return;
		}
		
		this.frame++;

		this.drawCurrentFrame();
    }

    render() {
        return (
			<div>
				<canvas className="stick-figure-canvas" ref="canvas" width={2000} height={1000} />
				{/* <button onClick={this.drawDance.bind(this)}>Play</button>  */}
			</div>
        );
    }
}

// To animate in Javascript, we use "requestAnimationFrame". 
// Read more here - https://developer.mozilla.org/en-US/docs/Web/API/window/requestAnimationFrame
const Canvas = ReactAnimationFrame(CanvasBase, 40);

export default Canvas;