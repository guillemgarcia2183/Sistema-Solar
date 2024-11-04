
vertex_shader_SUN ='''
                #version 330
                layout(location = 0) in vec3 in_norm;
                layout(location = 1) in vec3 in_position;
                layout(location = 2) in vec2 in_tex_coord;
                
                out vec3 v_norm;
                out vec3 v_frag_pos;
                out vec2 v_tex_coord; 

                uniform mat4 m_proj;
                uniform mat4 m_view;
                uniform mat4 m_model;

                void main() {
                    vec3 frag_pos = vec3(m_model * vec4(in_position, 1.0));
                    v_norm = normalize(mat3(transpose(inverse(m_model))) * in_norm);
                    v_frag_pos = frag_pos;
                    v_tex_coord = in_tex_coord;
                    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
                }
            '''
fragment_shader_SUN = '''
                #version 330
                in vec3 v_norm;
                in vec3 v_frag_pos;

                in vec2 v_tex_coord;

                out vec4 fragColor;
                struct Light {
                    vec3 position;
                    vec3 Ia;
                    vec3 Id;
                    vec3 Is;
                };

                uniform Light light;
                uniform vec3 view_pos;

                uniform sampler2D texture0;

                void main() {
                    vec3 norm = normalize(v_norm);
                    vec3 light_dir = normalize(light.position - v_frag_pos);
                    
                    // Ambient component
                    vec3 ambient = light.Ia;
                    
                    // Diffuse component
                    vec3 diffuse = light.Id * max(dot(norm, light_dir), 0.0);
                    
                    // Specular component
                    vec3 view_dir = normalize(view_pos - v_frag_pos);
                    vec3 reflect_dir = reflect(-light_dir, norm);
                    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);  // Shininess = 32
                    vec3 specular = light.Is * spec;

                    vec4 tex_color = texture(texture0, v_tex_coord);

                    // Combine all components
                    vec3 result = ambient + diffuse + specular;
                    fragColor = tex_color * vec4(result, 1.0);
                }
            '''

vertex_shader_PLANET ='''
                #version 330
                layout(location = 0) in vec3 in_norm;
                layout(location = 1) in vec3 in_position;
                layout(location = 2) in vec2 in_tex_coord;

                out vec3 v_norm;
                out vec3 v_frag_pos;
                out vec2 v_tex_coord;

                uniform mat4 m_proj;
                uniform mat4 m_view;
                uniform mat4 m_model;

                void main() {
                    vec3 frag_pos = vec3(m_model * vec4(in_position, 1.0));
                    v_norm = normalize(mat3(transpose(inverse(m_model))) * in_norm);
                    v_frag_pos = frag_pos;
                    v_tex_coord = in_tex_coord;
                    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
                }
            '''
fragment_shader_PLANET = '''
                #version 330
                in vec3 v_norm;
                in vec3 v_frag_pos;
                in vec2 v_tex_coord;

                out vec4 fragColor;
                struct Light {
                    vec3 position;
                    vec3 Ia;
                    vec3 Id;
                    vec3 Is;
                };

                uniform Light light;
                uniform vec3 view_pos;

                uniform sampler2D texture0;

                void main() {
                    vec3 norm = normalize(v_norm);
                    vec3 light_dir = normalize(light.position - v_frag_pos);
                    
                    // Ambient component
                    vec3 ambient = light.Ia;
                    
                    // Diffuse component
                    vec3 diffuse = light.Id * max(dot(norm, light_dir), 0.0);
                    
                    // Specular component
                    vec3 view_dir = normalize(view_pos - v_frag_pos);
                    vec3 reflect_dir = reflect(-light_dir, norm);
                    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);  // Shininess = 32
                    vec3 specular = light.Is * spec;

                    vec4 tex_color = texture(texture0, v_tex_coord);

                    // Combine all components
                    vec3 result = ambient + diffuse + specular;
                    fragColor = tex_color * vec4(result, 1.0);
                }
            '''

vertex_shader_STAR = '''
        #version 330

        layout(location = 0) in vec3 in_position;

        uniform mat4 m_proj;
        uniform mat4 m_view;
        uniform mat4 m_model;

        void main() {
            gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
        }
    '''
fragment_shader_STAR = '''
        #version 330

        uniform vec3 star_color;

        out vec4 fragColor;

        void main() {

            vec2 center = vec2(0.5);
            float inner_radius = 0.25;
            float outer_radius = 0.5;

            float distance = distance(gl_PointCoord, center);

            if (distance < inner_radius) {
                fragColor = vec4(star_color, 1.0);
            } else if (distance < outer_radius){
                fragColor = vec4(1.0, 1.0, 1.0, 1-distance/outer_radius);
            } else {
                discard;
            }
        }
    '''

vertex_shader_ELLIPSE = '''
        #version 330 core

        layout(location = 0) in vec3 in_position;

        uniform mat4 m_proj;   // Matriz de proyección
        uniform mat4 m_view;   // Matriz de vista
        uniform mat4 m_model;  // Matriz del modelo, que aquí sería la identidad

        void main() {
            // Transformación del vértice
            gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
        }
    '''
fragment_shader_ELLIPSE = '''
        #version 330 core

        out vec4 FragColor;

        uniform vec3 orbit_color;  // Color de la órbita, como un vector RGB

        void main() {
            // Define el color de la órbita
            FragColor = vec4(orbit_color, 1.0);  // Alpha de 1.0 para opacidad completa
        }

    '''

