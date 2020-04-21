import React, { Component } from "react";
import Canvas from "./canvas";

class DanceChooser extends Component {
	state = {
		loading: true,
		id: '',
		category: '',
		motion: '',
		apiRequestPath: 'Enter in an API request here to fetch'
	};

	componentDidMount() {
		this.loadFrames();
	}

	loadFrames = () => {
		this.callApi()
			.then(res => this.setState({ 
				id: res.id,
				category: res.category,
				motion: res.motion,
				loading: false
			}))
			.catch(err => console.log(err));
	}
	  
	callApi = async () => {
		this.setState({ loading: true });
		// TODO lol this code is so messy
		// EXAMPLE API REQUEST - '/api/dance/latin/3tST-Vz4Mx8_115'
		const apiRequestPath = this.state.apiRequestPath.includes("api/dance/") ? this.state.apiRequestPath : '/api/dance/gan/latin/70640182495117_sample1000.dance';
		const response = await fetch(apiRequestPath);
		// const response = await fetch('/api/dance/gan/latin/sample300_dance_ignoreme');
		const body = await response.json();
		if (response.status !== 200) throw Error(body.message);
		
		return body;
	}

	handleChange = (event) => {
		this.setState({apiRequestPath: event.target.value});
	}


	
	render() {
		if (this.state.loading) {
			return <h1>Loading...</h1>;
		}
		
		return (
			<div>
				<Canvas motion={this.state.motion} />
				<div className="info">
					<div><span>ID</span> { this.state.id }</div>
					<div><span>Category</span> { this.state.category }</div>
					<div>
						DEBUG
						<input value={this.state.apiRequestPath} onChange={this.handleChange}></input>
						<button onClick={this.loadFrames}>Load this Motion Sequence</button>
					</div>
				</div>
			</div>
		)
	}
}

export default DanceChooser;