import React from 'react';
import './App.css';
const data = require("./data/yimGp0XUcEE_motion.json");
// const data = require("./data/yimGp0XUcEE_motion.json");

// this is really bad janky code

const jawn = {"nose": 0,
"left_eye": 1,
"right_eye": 2,
"left_ear": 3,
"right_ear": 4,
"left_shoulder": 4,
"right_shoulder": 5,
"left_elbow": 6,
"right_elbow": 7,
"left_wrist": 8,
"right_wrist": 9,
"left_hip": 10,
"right_hip": 11,
"left_knee": 12,
"right_knee": 13,
"left_ankle": 14,
"right_ankle": 15 }

class Canvas extends React.Component {
  constructor(props) {
    super(props);
    this.state = { frame: 1 };
  }
  componentDidMount() {
    const canvas = this.refs.canvas
    this.ctx = canvas.getContext("2d");
    this.ctx.lineWidth = 10;
    // this.drawDance(data);

  }

  nextFrame() {
    this.drawFrame(this.state.frame);
    this.setState({
      frame: this.state.frame + 1
    });
  }

  drawDance() {
    this.setState({frame: 1 });
    for(let frame=1; frame<data.length; frame++) {
      setTimeout(() => {
        this.setState({frame: frame });
        this.drawFrame(frame);
      }, 70*frame);
    }
  }

  drawFrame(frame_no) {
    this.ctx.clearRect(0, 0, 2000, 1000);
    for(let p=0; p<data[frame_no].length; p++) {
        this.drawPerson(data[frame_no][p]);
    }
  }

  drawPerson(current) {
    // Nose 
    let nose = current[jawn.nose+1][0];
    let left_eye = current[jawn.left_eye+1][1];
    let right_eye = current[jawn.right_eye+1][1];
    let left_shoulder = current[jawn.left_shoulder+1][1];
    let right_shoulder = current[jawn.right_shoulder+1][1];
    let left_elbow = current[jawn.left_elbow+1][1];
    let right_elbow = current[jawn.right_elbow+1][1];
    let left_wrist = current[jawn.left_wrist+1][1];
    let right_wrist = current[jawn.right_wrist+1][1];
    let left_hip = current[jawn.left_hip+1][1];
    let right_hip = current[jawn.right_hip+1][1];
    let left_knee = current[jawn.left_knee+1][1];
    let right_knee = current[jawn.right_knee+1][1];
    let left_ankle = current[jawn.left_ankle+1][1];
    let right_ankle = current[jawn.right_ankle+1][1];

    //head
    let left_ear = current[jawn.left_ear+1][1];
    let right_ear = current[jawn.right_ear+1][1];
    let centerX = (left_ear[0] + right_ear[0])/2;
    let centerY = (left_ear[1] + right_ear[1])/2
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, 30, 0, 2 * Math.PI, false);
    this.ctx.fillStyle = 'black';
    this.ctx.fill();

    this.ctx.beginPath();
    this.ctx.moveTo(nose[0], nose[1]);
    this.ctx.lineTo(left_eye[0], left_eye[1]);
    this.ctx.lineTo(right_eye[0], right_eye[1]);
    this.ctx.lineTo(nose[0], nose[1]);
    this.ctx.stroke();
    this.ctx.beginPath();
    this.ctx.moveTo(left_shoulder[0], left_shoulder[1]);
    this.ctx.lineTo(left_elbow[0], left_elbow[1]);
    this.ctx.lineTo(left_wrist[0], left_wrist[1]);
    this.ctx.stroke();
    this.ctx.beginPath();
    this.ctx.moveTo(right_shoulder[0], right_shoulder[1]);
    this.ctx.lineTo(right_elbow[0], right_elbow[1]);
    this.ctx.lineTo(right_wrist[0], right_wrist[1]);
    this.ctx.stroke();
    this.ctx.beginPath();
    this.ctx.moveTo(right_hip[0], right_hip[1]);
    this.ctx.lineTo(right_knee[0], right_knee[1]);
    this.ctx.lineTo(right_ankle[0], right_ankle[1]);
    this.ctx.stroke();

    this.ctx.beginPath();
    this.ctx.moveTo(centerX, centerY);
    this.ctx.lineTo(left_hip[0], left_hip[1]);
    this.ctx.stroke();

    this.ctx.beginPath();
    this.ctx.moveTo(centerX, centerY);
    this.ctx.lineTo(right_hip[0], right_hip[1]);
    this.ctx.stroke();

    this.ctx.beginPath();
    this.ctx.moveTo(left_hip[0], left_hip[1]);
    this.ctx.lineTo(left_knee[0], left_knee[1]);
    this.ctx.lineTo(left_ankle[0], left_ankle[1]);
    this.ctx.stroke();
  }

  render() {
    return(
      <div>
        <canvas className="stick-figure-canvas" ref="canvas" width={2000} height={1000} />
        <button onClick={this.drawDance.bind(this)}>Play (the animation is fucked)</button> 
        <button onClick={this.nextFrame.bind(this)}>Draw Next Frame</button> 
        Frame { this.state.frame }
      </div>
    )
  }
}

function App() {
  return (
    <Canvas />
  );
}

export default App;
