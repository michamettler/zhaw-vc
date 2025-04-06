uniform sampler2D textureMap;
uniform sampler2D normalMap;

uniform float p_a; // ambienter Materialanteil
uniform float I_d; // diffuser Anteil der Lichtquelle
uniform float I_sp; // spekularer Anteil der Lichtquelle
uniform float shininess; // Shininess

in vec2 vUv; // Texturkoordinaten
in vec3 vLightDirTS; // Lichtvektor (Tangent Space)
in vec3 vViewDirTS; // Kameravektor (Tangent Space)

void main(void)
{
  vec3 baseColor = texture(textureMap, vUv).rgb;

  vec3 norm = texture(normalMap, vUv).xyz;
  norm = normalize(norm * 2.0 - 1.0);

  vec3 light = vLightDirTS;
  vec3 eye = vViewDirTS;

  // Berechnung gem. Anleitung
  vec3 halfVector = normalize(light + eye);

  float lambert = max(0.0, dot(norm, light));
  float phong = max(0.0, dot(norm, halfVector));
  float specularPower = pow(phong, shininess);

  float diffuse = I_d * lambert;
  float specular = I_sp * specularPower;

  vec3 I = p_a * baseColor + diffuse * baseColor + specular;

  gl_FragColor = vec4(I, 1.0);

}