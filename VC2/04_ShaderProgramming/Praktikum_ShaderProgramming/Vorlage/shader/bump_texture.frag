in vec2 vUv;
uniform sampler2D textureMap;

void main(void)
{
  gl_FragColor = texture2D(textureMap, vUv);
}