out vec2 vUv;
out vec3 vLightDirTS;
out vec3 vViewDirTS;

uniform vec3 lightPosition;

void main(void)
{
    vec3 worldPos = vec3(modelMatrix * vec4(position, 1.0));

    vec3 N = normalize(vec3(modelMatrix * vec4(normal, 0)));
    vec3 T = normalize(vec3(modelMatrix * vec4(1, 0, 0, 0)));
    vec3 B = normalize(cross(N, T));

    mat3 TBN = transpose(mat3(T, B, N));

    // Richtung zum Licht
    vec3 lightDirWorld = lightPosition - worldPos;
    vLightDirTS = normalize(TBN * normalize(lightDirWorld));

    // Richtung zur Kamera
    vec3 viewDirWorld = cameraPosition - worldPos;
    vViewDirTS = normalize(TBN * normalize(viewDirWorld));

    vUv = uv;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}