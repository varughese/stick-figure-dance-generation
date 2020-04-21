# Stick Figure Dance Generation

![https://imgur.com/prHrAVX.gif](https://imgur.com/prHrAVX.gif)

## What is this
As apart of our Deep Learning final term project, we attempted to use neural networks to teach a stick figure how to dance. Turned out to be pretty hard (especially since this was our first time using deep learning)

View our proposal for this project [here](https://docs.google.com/presentation/d/16DkyjuKUwEGn6KHBLAWM4mkfl6efR9skYgtHtZl7f50/edit#slide=id.p).

## Architecture
TODO - Insert our images

## Set Up
### Get  Data
1. Download the data from here - https://www.cc.gatech.edu/cpl/projects/dance/ and unzip it into the root directory
2. A little preprocessing to the data has to be done. If the dataset changes overtime, it might cause some small bugs.
```bash
cd preprocess && python save_frames_as_motion.py
```
The data is calculated pose data of people dancing.

### Run web app
This is a relatively simple + hacked web app used to visualize the dataset. Look online for how to set up `yarn`.
```bash
yarn global add concurrently
yarn install
cd frontend && yarn install
cd ..
yarn dev
```
The web app has a simple backend inn `server.js`, which pretty much just sends the frame data as JSON to the front end.
The front end is a React app that requests data from the backend, and animates the stick figures using `requestAnimationFrame` and drawing each person with lines.

### Train Neural Network
Everything related to generation is in the `gan` folder. 
```bash
cd gan
python train.py
```
