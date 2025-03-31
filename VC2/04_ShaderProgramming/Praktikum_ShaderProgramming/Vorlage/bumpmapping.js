import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

var scene, camera, renderer, controls, clock;
var texturePlane, heightPlane, normalPlane;

var bump_texture_vs, bump_texture_fs;
var bump_normal_vs, bump_normal_fs;
var bump_parallax_vs, bump_parallax_fs;

var viewerWidth, viewerHeight;

$(window).load(function(){
  SHADER_LOADER.load(
    function (data)
    {
        bump_texture_vs = data.bump_texture.vertex;
        bump_texture_fs = data.bump_texture.fragment;
        bump_normal_vs = data.bump_normal.vertex;
        bump_normal_fs = data.bump_normal.fragment;
        bump_parallax_vs = data.bump_parallax.vertex;
        bump_parallax_fs = data.bump_parallax.fragment;
        
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
  
  renderer.setClearColor(0xEEEEEE, 1.0);
  renderer.clear();        
  renderer.setSize( viewerWidth, viewerHeight );
  
  $("#viewer").append( renderer.domElement );
  
  camera.position.z = 40;
  
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

  // PLANE WITH TEXTURE
  var textureMaterial = new THREE.ShaderMaterial({
       vertexShader:   bump_texture_vs,
       fragmentShader: bump_texture_fs
   });

  texturePlane = new THREE.Mesh(new THREE.PlaneGeometry(15, 15, 100, 100), textureMaterial);
  texturePlane.position.set(-20,0,0);
  scene.add( texturePlane );
      
  // PLANE WITH NORMAL MAP
  var normalMaterial = new THREE.ShaderMaterial({
       vertexShader:   bump_normal_vs,
       fragmentShader: bump_normal_fs
   });

  heightPlane = new THREE.Mesh(new THREE.PlaneGeometry(15, 15, 100, 100), normalMaterial);
  heightPlane.position.set(0,0,0);
  scene.add( heightPlane );
       
  // PLANE WITH PARALLAX MAP
  var parallaxMaterial = new THREE.ShaderMaterial({
       vertexShader:   bump_parallax_vs,
       fragmentShader: bump_parallax_fs
   });
  normalPlane = new THREE.Mesh(new THREE.PlaneGeometry(15, 15, 100, 100), parallaxMaterial);
  normalPlane.position.set(20,0,0);
  scene.add( normalPlane );
}

function animate(){
  requestAnimationFrame(animate);
  render();
}

function render() {
  renderer.render(scene, camera);
}
