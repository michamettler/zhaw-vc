uniform vec3 lightPositionWS;

out vec3 vReflectWS;
out float vLambertWS;

void main() {
    vec3 posWS = (modelMatrix * vec4(position, 1.0)).xyz;
    vec3 normalWS = normalize(mat3(modelMatrix) * normal);

    vec3 viewDir = normalize(posWS - cameraPosition);
    vReflectWS = reflect(viewDir, normalWS);

    vec3 lightDir = normalize(lightPositionWS - posWS);
    vLambertWS = max(dot(normalWS, lightDir), 0.0);

    gl_Position = projectionMatrix * viewMatrix * vec4(posWS, 1.0);
}
