## Building/Running

Install Node, then run `npm install` in this folder to install the necessary dependecies.

To run:
- copy `.env.example` to a file named `.env`.
- after running the MQTT Broker (EMQX) fill the variable `REACT_APP_CLUSTERIP` with the output of `echo $(kubectl describe node | grep Addresses: -A 1 | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}")`
- fill the variable `REACT_APP_MQTTPORT` with the output of `echo $(kubectl get svc | grep emqx | grep NodePort | grep -oP ",8083:\K\d+(?=/TCP)")`
- `npm start` - Runs the app in the development mode. Opens [http://localhost:3000](http://localhost:3000) to view it in the browser.


- `npm test` - Launches the test runner in the interactive watch mode.
- `npm run build` - Builds the app for production in the `build` folder.