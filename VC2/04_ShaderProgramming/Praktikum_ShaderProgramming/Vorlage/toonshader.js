import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

var scene, camera, renderer, controls, clock;
var torus;  
var toon_vs, toon_fs;

var viewerWidth, viewerHeight;

$(window).load(function(){
    SHADER_LOADER.load(
        function (data)
        {
            toon_vs = data.toon.vertex;
            toon_fs = data.toon.fragment;
            
            viewerWidth = $("#viewer").innerWidth();
            viewerHeight = $("#viewer").innerHeight();

            initViewer();    
            animate(); 
        }
    );   
});

$(window).resize(function() {    
    
    camera.aspect = viewerWidth / viewerHeight;
    camera.updateProjectionMatrix();
    
    renderer.setSize( viewerWidth, viewerHeight );
});

function initViewer() {    
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera( 75, viewerWidth / viewerHeight, 0.1, 1000 );
    renderer = new THREE.WebGLRenderer();
    clock = new THREE.Clock;        
    controls = new OrbitControls( camera, renderer.domElement );

    renderer.setClearColor(0xEEEEEE, 1.0);
    renderer.clear();        
    renderer.setSize( viewerWidth, viewerHeight );

    $("#viewer").append( renderer.domElement );
        
    camera.position.z = 5;

    addHelpers();
    drawScene();
}

function addHelpers(){    
    var axes = new THREE.AxesHelper(50);
    axes.position.set(0, 0, 0);
    scene.add(axes);

    var gridXZ = new THREE.GridHelper(100, 10, new THREE.Color(0xFFC0CB), new THREE.Color(0x8f8f8f));
    gridXZ.position.set(0, 0, 0);
    scene.add(gridXZ);
}

function drawScene(){
    var shaderMaterial = new THREE.ShaderMaterial({
        vertexShader:   toon_vs,
        fragmentShader: toon_fs
    });

    torus = new THREE.Mesh(new THREE.TorusGeometry( 2, 0.5, 16, 50 ), shaderMaterial);
    torus.scale.set(1,1,1);
    torus.position.set(0, 0, 0);

    scene.add( torus );
}

function animate() {
    requestAnimationFrame(animate);
    render();
}

function render() {
    var delta = clock.getDelta();
    torus.rotation.x -= delta * 0.5;
    torus.rotation.y += delta * 0.5;
    renderer.render(scene, camera);
}
