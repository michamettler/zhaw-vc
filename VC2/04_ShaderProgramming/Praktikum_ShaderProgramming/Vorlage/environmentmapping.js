import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

var scene, camera, renderer, controls, clock;
var object, mesh;

var env_vs, env_fs;

var viewerWidth, viewerHeight;

$(window).load(function(){
  SHADER_LOADER.load(
    function (data)
    {
        env_vs = data.env.vertex;
        env_fs = data.env.fragment;
        
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
  var viewerWidth = $("#viewer").innerWidth();
  var viewerHeight = $("#viewer").innerHeight();
  
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera( 75, viewerWidth / viewerHeight, 0.1, 1000 );
  
  renderer = new THREE.WebGLRenderer();
  clock = new THREE.Clock;        
  controls = new OrbitControls( camera, renderer.domElement );
  
  renderer.setClearColor(0xEEEEEE, 1.0);
  renderer.clear();        
  renderer.setSize( viewerWidth, viewerHeight );
  
  camera.position.z = 30;
  camera.position.y = 20;
  camera.position.x = -10;
  
  camera.lookAt(new THREE.Vector3(0,0,0));
  
  $("#viewer").append( renderer.domElement );
   
  addHelpers();
  addLights();
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

function addLights(){
  var light = new THREE.AmbientLight( 0x111111 ); // soft white light
  scene.add( light );
  
  var directionalLight = new THREE.DirectionalLight( 0xFFFFFF );
  directionalLight.position.set( 1, -0.5, 1).normalize();
  scene.add( directionalLight );
}

function drawScene(){
  const cubeRenderTarget = new THREE.WebGLCubeRenderTarget( 512, { generateMipmaps: true, minFilter: THREE.LinearMipmapLinearFilter } );
  
  var shaderMaterial = new THREE.ShaderMaterial({
       vertexShader:   env_vs,
       fragmentShader: env_fs
   });

  object = new THREE.Mesh(new THREE.SphereGeometry( 5, 64, 64 ), shaderMaterial);
  object.scale.set(1,1,1);
  object.position.set(10, 5, 10);
  scene.add( object );
  
  drawReflectedObjects();
  drawSkybox();
}

function drawReflectedObjects(){    
  var donut = new THREE.Mesh(new THREE.TorusKnotGeometry( 10, 3, 100, 16 ), new THREE.MeshPhongMaterial({color : 0xFF0000}));
  donut.position.set(15, 0, 0);
  scene.add(donut);
  
  var donut2 = new THREE.Mesh(new THREE.CylinderGeometry( 5, 5, 20, 32 ), new THREE.MeshPhongMaterial({color : 0x00FF00}));
  donut2.position.set(-15, -5, 0);
  scene.add(donut2);
}

function drawSkybox() {    
  var urls = [
    "textures/dunes_right.jpg",
    "textures/dunes_left.jpg",
    "textures/dunes_top.jpg",
    "textures/dunes_bottom.jpg",
    "textures/dunes_front.jpg",
    "textures/dunes_back.jpg"
  ];
  var textureCube = new THREE.CubeTextureLoader().load( urls );
      
  var uniforms = THREE.UniformsUtils.clone(THREE.ShaderLib.cube.uniforms);
  uniforms.tCube.value = textureCube;

  var material = new THREE.ShaderMaterial( {
      fragmentShader: THREE.ShaderLib.cube.fragmentShader,
      vertexShader: THREE.ShaderLib.cube.vertexShader,
      uniforms: uniforms,
      depthWrite: false,
      side: THREE.BackSide
  } );
  Object.defineProperty(material, 'envMap', {
    get: function() {
      return textureCube;
    }
  });

  mesh = new THREE.Mesh( new THREE.BoxGeometry( 1000, 1000, 1000 ), material );
  scene.add( mesh );
}

function animate(){    
  requestAnimationFrame(animate);
  render();
}

function render() {
  var elapsed = clock.getElapsedTime() / 2.0;
  
  object.position.z = Math.cos(elapsed) * 25;
  object.position.x = Math.sin(elapsed) * 25;
  renderer.render(scene, camera);
}
