in vec3 vNormalWorld;
uniform vec3 lightDirection;

void main(void)
{
    vec3 normal = normalize(vNormalWorld);
    vec3 lightDir = normalize(lightDirection);

    // Skalarprodukt berechnen
    float dotNL = max(dot(normal, lightDir), 0.0);

    vec4 color;

     if (dotNL > 0.8) {
        color = vec4(0.8, 0.8, 1.0, 1.0);
    }
    else if (dotNL > 0.6) {
        color = vec4(0.3, 0.3, 0.6, 1.0);
    }
    else if (dotNL > 0.3) {
        color = vec4(0.2, 0.2, 0.4, 1.0);
    }
    else {
        color = vec4(0.1, 0.1, 0.2, 1.0);
    }

    gl_FragColor  = color;
    
}