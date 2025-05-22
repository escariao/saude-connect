// API client para o Saúde Connect
window.api = {
    // URL base da API
    baseUrl: '/api',
    
    // Método para verificar se o usuário está autenticado
    isAuthenticated: function() {
        try {
            const token = localStorage.getItem('token');
            const userData = localStorage.getItem('userData');
            return !!(token && userData && JSON.parse(userData));
        } catch (error) {
            console.error('Erro ao verificar autenticação:', error);
            // Em caso de erro, considerar que não está autenticado
            localStorage.removeItem('token');
            localStorage.removeItem('userData');
            return false;
        }
    },
    
    // Método para obter o tipo de usuário
    getUserType: function() {
        try {
            const userData = localStorage.getItem('userData');
            if (!userData) return null;
            
            const user = JSON.parse(userData);
            return user.user_type;
        } catch (error) {
            console.error('Erro ao obter tipo de usuário:', error);
            return null;
        }
    },
    
    // Método para obter os dados do usuário
    getUserData: function() {
        try {
            const userData = localStorage.getItem('userData');
            if (!userData) return null;
            
            return JSON.parse(userData);
        } catch (error) {
            console.error('Erro ao obter dados do usuário:', error);
            return null;
        }
    },
    
    // Método para fazer login
    login: async function(email, password) {
        try {
            const response = await fetch(`${this.baseUrl}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Erro ao fazer login');
            }
            
            // Armazenar token e dados do usuário
            localStorage.setItem('token', data.token);
            localStorage.setItem('userData', JSON.stringify(data.user));
            
            return data;
        } catch (error) {
            console.error('Erro no login:', error);
            throw error;
        }
    },
    
    // Método para fazer logout
    logout: function() {
        localStorage.removeItem('token');
        localStorage.removeItem('userData');
    },
    
    // Método para cadastrar paciente
    registerPatient: async function(patientData) {
        try {
            const response = await fetch(`${this.baseUrl}/patient/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(patientData)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Erro ao cadastrar paciente');
            }
            
            return data;
        } catch (error) {
            console.error('Erro no cadastro de paciente:', error);
            throw error;
        }
    },
    
    // Método para cadastrar profissional
    registerProfessional: async function(professionalData) {
        try {
            // Criar FormData para envio de arquivos
            const formData = new FormData();
            
            // Adicionar dados do profissional
            Object.keys(professionalData).forEach(key => {
                if (key !== 'diploma') {
                    formData.append(key, professionalData[key]);
                }
            });
            
            // Adicionar diploma se existir
            if (professionalData.diploma) {
                formData.append('diploma', professionalData.diploma);
            }
            
            const response = await fetch(`${this.baseUrl}/professional/register`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Erro ao cadastrar profissional');
            }
            
            return data;
        } catch (error) {
            console.error('Erro no cadastro de profissional:', error);
            throw error;
        }
    },
    
    // Método para buscar categorias
    getCategories: async function() {
        try {
            const response = await fetch(`${this.baseUrl}/search/categories`);
            
            if (!response.ok) {
                throw new Error('Erro ao buscar categorias');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao buscar categorias:', error);
            throw error;
        }
    },
    
    // Método para buscar atividades
    getActivities: async function(categoryId = null) {
        try {
            let url = `${this.baseUrl}/search/activities`;
            if (categoryId) {
                url += `?category_id=${categoryId}`;
            }
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error('Erro ao buscar atividades');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao buscar atividades:', error);
            // Retornar array vazio em caso de erro para evitar quebra da interface
            return [];
        }
    },
    
    // Método para buscar profissionais
    searchProfessionals: async function(params = {}) {
        try {
            // Construir query string
            const queryParams = new URLSearchParams();
            Object.keys(params).forEach(key => {
                if (params[key]) {
                    queryParams.append(key, params[key]);
                }
            });
            
            const url = `${this.baseUrl}/search/professionals?${queryParams.toString()}`;
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error('Erro ao buscar profissionais');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao buscar profissionais:', error);
            throw error;
        }
    },
    
    // Método para obter dados do perfil do paciente
    getPatientProfile: async function() {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Usuário não autenticado');
            }
            
            const userData = this.getUserData();
            if (!userData || !userData.id) {
                throw new Error('Dados do usuário não encontrados');
            }
            
            const response = await fetch(`${this.baseUrl}/patient/${userData.id}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Erro ao buscar perfil do paciente');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao buscar perfil do paciente:', error);
            throw error;
        }
    },
    
    // Método para obter dados do perfil do profissional
    getProfessionalProfile: async function() {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Usuário não autenticado');
            }
            
            const userData = this.getUserData();
            if (!userData || !userData.id) {
                throw new Error('Dados do usuário não encontrados');
            }
            
            const response = await fetch(`${this.baseUrl}/professional/${userData.id}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Erro ao buscar perfil do profissional');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao buscar perfil do profissional:', error);
            throw error;
        }
    },
    
    // Método para atualizar perfil do paciente
    updatePatientProfile: async function(profileData) {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Usuário não autenticado');
            }
            
            const userData = this.getUserData();
            if (!userData || !userData.id) {
                throw new Error('Dados do usuário não encontrados');
            }
            
            const response = await fetch(`${this.baseUrl}/patient/${userData.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(profileData)
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Erro ao atualizar perfil');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao atualizar perfil do paciente:', error);
            throw error;
        }
    },
    
    // Método para atualizar perfil do profissional
    updateProfessionalProfile: async function(profileData) {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Usuário não autenticado');
            }
            
            const userData = this.getUserData();
            if (!userData || !userData.id) {
                throw new Error('Dados do usuário não encontrados');
            }
            
            // Criar FormData para envio de arquivos
            const formData = new FormData();
            
            // Adicionar dados do profissional
            Object.keys(profileData).forEach(key => {
                if (key !== 'diploma' || (key === 'diploma' && profileData[key] instanceof File)) {
                    formData.append(key, profileData[key]);
                }
            });
            
            const response = await fetch(`${this.baseUrl}/professional/${userData.id}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Erro ao atualizar perfil');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao atualizar perfil do profissional:', error);
            throw error;
        }
    },
    
    // Método para adicionar atividade (admin)
    addActivity: async function(activityData) {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Usuário não autenticado');
            }
            
            const response = await fetch(`${this.baseUrl}/admin/activities`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(activityData)
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Erro ao adicionar atividade');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao adicionar atividade:', error);
            throw error;
        }
    },
    
    // Método para listar profissionais pendentes (admin)
    getPendingProfessionals: async function() {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Usuário não autenticado');
            }
            
            const response = await fetch(`${this.baseUrl}/admin/professionals/pending`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Erro ao buscar profissionais pendentes');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao buscar profissionais pendentes:', error);
            throw error;
        }
    },
    
    // Método para aprovar profissional (admin)
    approveProfessional: async function(professionalId) {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Usuário não autenticado');
            }
            
            const response = await fetch(`${this.baseUrl}/admin/professionals/${professionalId}/approve`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Erro ao aprovar profissional');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao aprovar profissional:', error);
            throw error;
        }
    },
    
    // Método para rejeitar profissional (admin)
    rejectProfessional: async function(professionalId) {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Usuário não autenticado');
            }
            
            const response = await fetch(`${this.baseUrl}/admin/professionals/${professionalId}/reject`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Erro ao rejeitar profissional');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao rejeitar profissional:', error);
            throw error;
        }
    }
};
