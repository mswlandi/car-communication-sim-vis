import React, {useRef, useEffect, useState} from 'react';
import maplibregl from 'maplibre-gl';
import './map.css';
import 'maplibre-gl/dist/maplibre-gl.css';
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader'
import { useSubscription } from 'mqtt-react-hooks';


// uses the longitude and latitude of the model to give its position in threejs coordinates
// uses the center of the rendering layer as reference for translating, and scaling according to the latitude
function getPositionFromLongLat(center, carData){
    
    var centerCoords = maplibregl.MercatorCoordinate.fromLngLat(center.LngLat, 0);
    var objectCoords = maplibregl.MercatorCoordinate.fromLngLat(carData.LngLat, 0);
    
    var dx = centerCoords.x - objectCoords.x;
    var dy = centerCoords.y - objectCoords.y;
    
    dx /= center.scale;
    dy /= center.scale;

    return new THREE.Vector3(-dx, 0, -dy);
}


// loads a GLTF 3D model of a car into the threejs scene
function loadGLTFModel(scene, center, carData) {
    return new Promise((resolve, reject) => {
        const dracoLoader = new DRACOLoader();
        dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.5/');
        const loader = new GLTFLoader();
        loader.setDRACOLoader(dracoLoader);

        const position = getPositionFromLongLat(center, carData);

        loader.load(
            // ferrari1.glb: original model, 1.7 MB
            // ferrari2.glb: just a Parallelepiped
            // ferrari3.glb: decimated version of original model, 0.57 MB
            process.env.PUBLIC_URL + "/ferrari3.glb",
            (gltf) => {
                const obj = gltf.scene;
                obj.position.set(position.x, position.y, position.z);
                obj.rotation.set(carData.rotateX, carData.rotateY, carData.rotateZ);
                obj.receiveShadow = false;
                obj.castShadow = false;
                scene.add(obj);

                obj.traverse(function(child) {
                    if(child.isMesh) {
                        child.castShadow = false;
                        child.receiveShadow = false;
                    }
                });

                resolve(obj);
            },
            undefined,
            function(error) {
                console.log(error);
                reject(error);
            }
        );
    });
}


export default function Map(props) {
    const mapContainer = useRef(null);
    const [carData2] = useState({
        id: "second_car", // test car 2
        LngLat: [9.106607, 48.744746],
        altitude: 0,
        rotateX: 0,
        rotateY: 3 * Math.PI / 8, // Actual desired car rotation
        rotateZ: 0
    });
    const [zoom] = useState(21);
    const [API_KEY] = useState('cqvAKHMBJexanBFc1owH ');

    const { message } = useSubscription([
        'carInfo/+/update',
        'carInfo/+/close'
    ]);
    
    const [lat] = useState(48.744715);
    const [lng] = useState(9.1066383);
    const [centerMercator] = useState(maplibregl.MercatorCoordinate.fromLngLat([lng, lat]));
    const [center] = useState({
        LngLat: [lng, lat],
        translateX: centerMercator.x,
        translateY: centerMercator.y,
        translateZ: centerMercator.z,
        rotateX: Math.PI / 2,
        rotateY: 0,
        rotateZ: 0,
        scale: centerMercator.meterInMercatorCoordinateUnits()
    });

    // maps car id to whether a 3D Object is being created for it
    const [carObjBeingCreated, setCarObjBeingCreated] = useState({});
    const [carDataList, setCarDataList] = useState([]);
    const [scene, setScene] = useState(new THREE.Scene());

    // updates information about car, if car doesn't exist in the car data array, adds it to the array.
    // will make a bunch of stuff even if no actual information about the car has changed
    // TODO:
    // - check if changes were made
    // - only change present fields
    function updateCarData(carData) {
        if (!carData.id) {
            console.log("requested car data update doesn't provide car ID");
            return false;
        }

        function updateState(carData, carIndexInList) {
            setCarDataList((oldList => {
                const updatedCarDataList = [...oldList];
    
                if (carIndexInList === -1) {
                    updatedCarDataList.push(carData);
                } else {
                    // console.log(`car data for car ID ${carData.id} updated.`);
                    updatedCarDataList.splice(carIndexInList, 1, carData);
                }
    
                return updatedCarDataList;
            }));
        }

        var carIndexInList = carDataList.findIndex((value, index, array) => {return carData.id === value.id});

        // didn't find carData in list and obj is not being created
        if (carIndexInList === -1 && !carObjBeingCreated[carData.id]) {
            setCarObjBeingCreated(oldObj => {
                oldObj[carData.id] = true;
                return oldObj;
            });
            // creates 3D model
            loadGLTFModel(scene, center, carData)
            .then((object) => {
                console.log(`model loaded for car ${carData.id}`);
                carData.obj = object;
                carData.objIsCreating = false;
                updateState(carData, carIndexInList);
                setCarObjBeingCreated(oldObj => {
                    oldObj[carData.id] = false;
                    return oldObj;
                });
            });
        // if carData is in list (and therefore also has an obj)
        } else if (carIndexInList !== -1) {
            const position = getPositionFromLongLat(center, carData);
            
            const obj = carDataList[carIndexInList].obj;
            
            if (obj !== undefined) {
                obj.position.set(position.x, position.y, position.z);
                obj.rotation.set(carData.rotateX, carData.rotateY, carData.rotateZ);
                
                carData.obj = obj;
                updateState(carData, carIndexInList);
            }
        }
        else {
            // didn't perform any changes to the list
            return false;
        }

        return true;
    }

    // destroys 3D object of car and remove its data from the list
    function deleteCar(carID) {

        // helper recursive function to remove all nested 3D objects
        function removeObjectsWithChildren(obj) {
            if(obj.children.length > 0){
                for (var x = obj.children.length - 1; x>=0; x--){
                    removeObjectsWithChildren( obj.children[x]);
                }
            }

            if (obj.geometry) {
                obj.geometry.dispose();
            }

            if (obj.material) {
                if (obj.material.length) {
                    for (let i = 0; i < obj.material.length; ++i) {

                        if (obj.material[i].map) obj.material[i].map.dispose();
                        if (obj.material[i].lightMap) obj.material[i].lightMap.dispose();
                        if (obj.material[i].bumpMap) obj.material[i].bumpMap.dispose();
                        if (obj.material[i].normalMap) obj.material[i].normalMap.dispose();
                        if (obj.material[i].specularMap) obj.material[i].specularMap.dispose();
                        if (obj.material[i].envMap) obj.material[i].envMap.dispose();

                        obj.material[i].dispose()
                    }
                }
                else {
                    if (obj.material.map) obj.material.map.dispose();
                    if (obj.material.lightMap) obj.material.lightMap.dispose();
                    if (obj.material.bumpMap) obj.material.bumpMap.dispose();
                    if (obj.material.normalMap) obj.material.normalMap.dispose();
                    if (obj.material.specularMap) obj.material.specularMap.dispose();
                    if (obj.material.envMap) obj.material.envMap.dispose();

                    obj.material.dispose();
                }
            }

            obj.removeFromParent();

            return true;
        }
        
        var carIndexInList = carDataList.findIndex((value, index, array) => {return carID === value.id});

        setCarDataList((oldList => {
            const updatedCarDataList = [...oldList];

            if (carIndexInList === -1) {
                console.log(`tried removing car that doesn't exist: ${carID}`);
            } else {
                console.log(`destroyed obj for car ${carID}`);
                removeObjectsWithChildren(carDataList[carIndexInList].obj);
                updatedCarDataList.splice(carIndexInList, 1);
            }

            return updatedCarDataList;
        }));

    }

    // runs on message updates
    useEffect(() => {
        if (message) {
            if (message.topic.endsWith("/update")) {
                const carData = JSON.parse(message.message);
                updateCarData(carData);
            }
            else if (message.topic.endsWith("/close")) {
                const carID = message.topic.split('/')[1];
                console.log(`connection with ${carID} closed`);
                deleteCar(carID);
            }
        }
    }, [message]);

    // map initialization
    useEffect(() => {
        if (props.map.current) 
            return;
        
        props.map.current = new maplibregl.Map({
            container: mapContainer.current,
            style: `https://api.maptiler.com/maps/streets/style.json?key=${API_KEY}`,
            center: [lng, lat],
            zoom: zoom,
            pitch: 60,
            maxPitch: 85,
            antialias: true
        });

        // ----------- 1ST MODEL DATA ---------------------
        // transformation parameters to position, rotate and scale the 3D model onto the map
        var carData1 = {
            id: "first_car", // test car 1
            LngLat: [9.106596, 48.744459],
            altitude: 0,
            rotateX: 0,
            rotateY: 5.5 * Math.PI / 8, // Actual desired car rotation
            rotateZ: 0
        };
        // ------------------------------------------------

        // create a custom style layer for the map to implement the threejs WebGL content
        var customCarLayer = {
            id: 'threedee',
            type: 'custom',
            renderingMode: '3d',

            addLights: function (scene) {
                // create two three.js lights to illuminate the model
                var directionalLight = new THREE.DirectionalLight(0xffffff);
                directionalLight.position.set(0, -70, 100).normalize();
                scene.add(directionalLight);

                var directionalLight2 = new THREE.DirectionalLight(0xffffff);
                directionalLight2.position.set(0, 70, 100).normalize();
                scene.add(directionalLight2);

                return scene;
            },

            // method called when the layer is added to the map
            // https://maplibre.org/maplibre-gl-js-docs/api/properties/#styleimageinterface#onadd
            onAdd: function (map, gl) {
                this.camera = new THREE.Camera();
                setScene((oldScene) => {
                    this.addLights(oldScene);
                    return oldScene;
                });
                this.map = map;
                
                // updateCarData(carData1);
                // updateCarData(carData2);

                // use the MapLibre GL JS map canvas for three.js
                this.renderer = new THREE.WebGLRenderer({
                    canvas: map.getCanvas(),
                    context: gl,
                    antialias: true
                });

                this.renderer.autoClear = false;
            },

            // method fired on each animation frame
            // https://maplibre.org/maplibre-gl-js-docs/api/map/#map.event:render
            render: function (gl, matrix) {
                var rotationX = new THREE.Matrix4().makeRotationAxis(new THREE.Vector3(1, 0, 0), center.rotateX);
                var rotationY = new THREE.Matrix4().makeRotationAxis(new THREE.Vector3(0, 1, 0), center.rotateY);
                var rotationZ = new THREE.Matrix4().makeRotationAxis(new THREE.Vector3(0, 0, 1), center.rotateZ);

                var m = new THREE.Matrix4().fromArray(matrix);
                
                var l = new THREE.Matrix4().makeTranslation(center.translateX, center.translateY, center.translateZ)
                .scale(new THREE.Vector3(center.scale, -center.scale, center.scale))
                .multiply(rotationX)
                .multiply(rotationY)
                .multiply(rotationZ);

                this.camera.projectionMatrix.elements = matrix;
                this.camera.projectionMatrix = m.multiply(l);

                this.renderer.state.reset();
                this.renderer.render(scene, this.camera);
                this.map.triggerRepaint();
            }
        };

        // add the custom style layer to the map
        props.map.current.on('style.load', function () {
            props.map.current.addLayer(customCarLayer);
        });
    });

    const animateCar = function () {
        var newCarData = {...carData2, LngLat: [9.106625, 48.744658]};
        updateCarData(newCarData);
    };

    return (
    <div className="map-wrap">
        <div ref={mapContainer}
            className="map"/>
        {/* <button onClick={() => animateCar()}>animate</button> */}
        {/* <button onClick={() => console.log(carDataList)}>print</button> */}
        {/* <div>{`topic:${message ? message.topic : 'empty'} - message: ${message ? message.message : 'empty'}`}</div> */}
    </div>
    );
}
