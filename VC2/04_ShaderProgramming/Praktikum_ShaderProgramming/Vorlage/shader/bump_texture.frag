in vec2 vUv;
uniform sampler2D tex;

void main(void)
{
  gl_FragColor = texture2D(tex, vUv);
}