#version 330 

out vec4 fragColor;

void main() {
    vec3 color = vec3(1.0);
    fragColor = vec4(color, 1.0);
}
