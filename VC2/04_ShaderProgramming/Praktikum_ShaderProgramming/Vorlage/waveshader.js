import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

var scene, camera, renderer, controls, clock;
var plane, light;
var wave_vs, wave_fs;

var viewerWidth, viewerHeight;

$(window).load(function() {
  SHADER_LOADER.load(
    function (data)
    {
        wave_vs = data.wave.vertex;
        wave_fs = data.wave.fragment;
        
        viewerWidth = $("#viewer").innerWidth();
        viewerHeight = $("#viewer").innerHeight();
    
        initViewer();
        animate();
    }
  );   
});
  
$( window ).resize(function() {
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
  controls.damping = 0.2;
  controls.addEventListener('change', render);
  
  renderer.setClearColor(0xEEEEEE, 1.0);
  renderer.clear();        
  renderer.setSize( viewerWidth, viewerHeight );
  
  $("#viewer").append( renderer.domElement );
   
  camera.position.z = 20;
  camera.position.y = 20;
  
  addHelpers();
  drawScene();
}

function addHelpers(){    
  var axes = new THREE.AxesHelper(50);
  axes.position.set(0,0,0);
  scene.add(axes);

  var gridXZ = new THREE.GridHelper(100, 10, new THREE.Color(0xFFC0CB), new THREE.Color(0x8f8f8f));
  gridXZ.position.set(0,0,0 );
  scene.add(gridXZ);
}

function drawScene(){
  var settings = {
    ambientColor: { x: .4, y: .3, z: .2 },
    diffuseColor: { x: .4, y: .4, z: .4 },
    specularColor: { x: .6, y: .6, z: .6 },
    shininess: 10
  };
  
  var shaderMaterial = new THREE.ShaderMaterial({
      vertexShader:   wave_vs,
      fragmentShader: wave_fs
  });

  plane = new THREE.Mesh(new THREE.PlaneGeometry(100, 100, 100, 100), shaderMaterial);
  plane.rotation.x = -0.5 * Math.PI;
  plane.position.set(0, 0, 0);
  
  light = new THREE.Mesh(new THREE.SphereGeometry(2, 16, 16), new THREE.MeshBasicMaterial({color: 0x00FFFF}));
  light.position.set(20.0, 20.0, 30.0);
  scene.add(light);
  
  scene.add( plane );
}

function animate() {
  requestAnimationFrame(animate);
  render();
}

function render() {
  renderer.render(scene, camera);
}
