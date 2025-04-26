uniform samplerCube envMap;
uniform float mixRatio;
uniform vec3 baseColor;

in vec3 vReflectWS;
in float vLambertWS;

void main() {
    vec3 reflected = textureCube(envMap, normalize(vReflectWS)).rgb;
    vec3 diffuse = baseColor * vLambertWS;
    vec3 finalColor = mix(reflected, diffuse, mixRatio);

    gl_FragColor = vec4(finalColor, 1.0);
}
