#version 330

uniform vec3 star_color;

out vec4 fragColor;

void main() {
    if (distance(gl_PointCoord, vec2(0.5, 0.5)) > 0.5) {
        discard;
    }
    fragColor = vec4(star_color, 1.0);
}
