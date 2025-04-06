out vec3 vNormalWorld;

void main() {
    vNormalWorld = normalize(mat3(modelMatrix) * normal);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}