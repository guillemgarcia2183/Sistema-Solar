vertex_shader_SUN ='''
                #version 330
                layout(location = 0) in vec3 in_color;
                layout(location = 1) in vec3 in_norm;
                layout(location = 2) in vec3 in_position;
                
                out vec3 v_color;
                out vec3 v_norm;
                out vec3 v_frag_pos;

                uniform mat4 m_proj;
                uniform mat4 m_view;
                uniform mat4 m_model;

                void main() {
                    vec3 frag_pos = vec3(m_model * vec4(in_position, 1.0));
                    v_norm = normalize(mat3(transpose(inverse(m_model))) * in_norm);
                    v_frag_pos = frag_pos;
                    v_color = in_color;
                    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
                }
            '''
fragment_shader_SUN ='''
                #version 330
                in vec3 v_color;
                in vec3 v_norm;
                in vec3 v_frag_pos;

                out vec4 fragColor;
                struct Light {
                    vec3 position;
                    vec3 Ia;
                    vec3 Id;
                    vec3 Is;
                };

                uniform Light light;  

                uniform vec3 view_pos;

                void main() {
                    vec3 norm = normalize(v_norm);
                    vec3 light_dir = normalize(light.position - v_frag_pos);
                    
                    // Ambient component
                    vec3 ambient = light.Ia;
                    
                    // Diffuse component
                    vec3 diffuse = light.Id * max(dot(norm, light_dir), 0.0) * v_color;
                    
                    // Specular component
                    vec3 view_dir = normalize(view_pos - v_frag_pos);
                    vec3 reflect_dir = reflect(-light_dir, norm);
                    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);  // Shininess = 32
                    vec3 specular = light.Is * spec;

                    // Combine all components
                    vec3 result = ambient + diffuse + specular; 
                    fragColor = vec4(result, 1.0);
                }
            '''

vertex_shader_EARTH ='''
                #version 330
                layout(location = 0) in vec3 in_color;
                layout(location = 1) in vec3 in_norm;
                layout(location = 2) in vec3 in_position;
                
                out vec3 v_color;
                out vec3 v_norm;
                out vec3 v_frag_pos;

                uniform mat4 m_proj;
                uniform mat4 m_view;
                uniform mat4 m_model;

                void main() {
                    vec3 frag_pos = vec3(m_model * vec4(in_position, 1.0));
                    v_norm = normalize(mat3(transpose(inverse(m_model))) * in_norm);
                    v_frag_pos = frag_pos;
                    v_color = in_color;
                    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
                }
            '''
fragment_shader_EARTH = '''
                #version 330
                in vec3 v_color;
                in vec3 v_norm;
                in vec3 v_frag_pos;

                out vec4 fragColor;
                struct Light {
                    vec3 position;
                    vec3 Ia;
                    vec3 Id;
                    vec3 Is;
                };

                uniform Light light;
                uniform int phong;   

                uniform vec3 view_pos;

                void main() {
                    vec3 norm = normalize(v_norm);
                    vec3 light_dir = normalize(light.position - v_frag_pos);
                    
                    // Ambient component
                    vec3 ambient = light.Ia;
                    
                    // Diffuse component
                    vec3 diffuse = light.Id * max(dot(norm, light_dir), 0.0) * v_color;
                    
                    // Specular component
                    vec3 view_dir = normalize(view_pos - v_frag_pos);
                    vec3 reflect_dir = reflect(-light_dir, norm);
                    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);  // Shininess = 32
                    vec3 specular = light.Is * spec;

                    // Combine all components
                    vec3 result = ambient + diffuse + specular;
                    fragColor = vec4(result, 1.0);
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
            if (distance(gl_PointCoord, vec2(0.5, 0.5)) > 0.5) {
                discard;
            }
            fragColor = vec4(star_color, 1.0);
        }
    '''