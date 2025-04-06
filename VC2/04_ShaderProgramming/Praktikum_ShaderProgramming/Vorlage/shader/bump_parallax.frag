uniform sampler2D textureMap;
uniform sampler2D heightMap;
uniform sampler2D normalMap;

uniform float scale;
uniform float bias;

uniform float p_a; // ambienter Materialanteil
uniform float I_d; // diffuser Anteil der Lichtquelle
uniform float I_sp; // spekularer Anteil der Lichtquelle
uniform float shininess; // Shininess

in vec2 vUv;
in vec3 vLightDirTS; // Lichtvektor (Tangent Space)
in vec3 vViewDirTS; // Kameravektor (Tangent Space)

void main() {
    float height = texture(heightMap, vUv).r;

    float hsb = height * scale + bias;
    vec2 newUv = vUv + hsb * vViewDirTS.xy;

    // analog zu normal mapping
    vec3 baseColor = texture2D(textureMap, newUv).rgb;

    vec3 norm = texture2D(normalMap, newUv).xyz;
    norm = normalize(norm * 2.0 - 1.0);

    vec3 light = normalize(vLightDirTS);
    vec3 eye = normalize(vViewDirTS);

    vec3 halfVector = normalize(light + eye);
    float lambert = max(0.0, dot(norm, light));
    float phong = max(0.0, dot(norm, halfVector));
    float specularPower = pow(phong, shininess);

    float diffuse = I_d * lambert;
    float specular = I_sp * specularPower;

    vec3 I = p_a * baseColor + diffuse * baseColor + specular;

    gl_FragColor = vec4(I, 1.0);
}
