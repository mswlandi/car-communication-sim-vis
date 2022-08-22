import React, { useEffect, useRef, useState } from 'react';
import ReactDOM from 'react-dom/client';

import { Connector, useSubscription } from 'mqtt-react-hooks';

import './index.css';
import Navbar from './navbar.js';
import Map from './map.js';

window.Buffer = window.Buffer || require("buffer").Buffer; 

window.process = {
    env: {
        NODE_ENV: 'development'
    }
}

// const mqtt = require('mqtt');
// const client = mqtt.connect('http://172.18.0.2:30751');

// client.on('connect', () => {
//     client.subscribe('carInfo/update', function (err) {
//         if (!err) {
//             console.log('connected to MQTT server');
//         }
//     })
// });

// client.on('message', function (topic, message) {
//     // message is Buffer
//     console.log(message.toString());
//     client.end();
// })

export default function Status() {
    /* Message structure:
     *  topic: string
     *  message: string
     */
    const { message } = useSubscription([
      'carInfo/update',
    ]);
  
    return (
      <>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span>{`topic:${message.topic} - message: ${message.message}`}</span>
        </div>
      </>
    );
  }

const Dashboard = () => {

    const map = useRef(null);

    return (
        <div>
            <Navbar />
            {/* <Map map={map}/> */}
            <Connector brokerUrl="http://172.18.0.2:30751">
                <Status />
            </Connector>
        </div>
    )
}

// ========================================

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<Dashboard />);
