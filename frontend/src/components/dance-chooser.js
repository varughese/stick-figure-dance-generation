import React, { Component } from "react";
import Canvas from "./canvas";

class DanceChooser extends Component {
	state = {
		loading: true,
		id: '',
		category: '',
		motion: ''
	};

	componentDidMount() {
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
		// const response = await fetch('/api/dance/latin/3tST-Vz4Mx8_115');
		const response = await fetch('api/dance/gan/latin/3tST-Vz4Mx8_115_test');
		const body = await response.json();
		if (response.status !== 200) throw Error(body.message);
		
		return body;
	};
	
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
				</div>
			</div>
		)
	}
}

export default DanceChooser;