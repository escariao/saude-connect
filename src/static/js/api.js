// API client para o Saúde Connect

const API_BASE_URL = '';

window.api = {
    // Autenticação
    login: async function(email, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Falha na autenticação');
            }
            
            const data = await response.json();
            localStorage.setItem('token', data.token);
            localStorage.setItem('userData', JSON.stringify(data.user));
            
            return data;
        } catch (error) {
            console.error('Erro no login:', error);
            throw error;
        }
    },
    
    logout: function() {
        localStorage.removeItem('token');
        localStorage.removeItem('userData');
    },
    
    isAuthenticated: function() {
        return !!localStorage.getItem('token');
    },
    
    getUserData: function() {
        const userData = localStorage.getItem('userData');
        return userData ? JSON.parse(userData) : null;
    },
    
    getToken: function() {
        return localStorage.getItem('token');
    },
    
    // Cadastros
    registerPatient: async function(patientData) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/patient/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(patientData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Falha no cadastro');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro no cadastro de paciente:', error);
            throw error;
        }
    },
    
    registerProfessional: async function(formData) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/user/register_professional`, {
                method: 'POST',
                body: formData // FormData já está configurado para multipart/form-data
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Falha no cadastro');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro no cadastro de profissional:', error);
            throw error;
        }
    },
    
    // Atividades e Categorias
    getActivities: async function() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/search/activities`);
            
            if (!response.ok) {
                throw new Error('Falha ao buscar atividades');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao buscar atividades:', error);
            throw error;
        }
    },
    
    getCategories: async function() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/admin/categories`);
            
            if (!response.ok) {
                throw new Error('Falha ao buscar categorias');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao buscar categorias:', error);
            throw error;
        }
    },
    
    createCategory: async function(categoryData) {
        try {
            const token = this.getToken();
            if (!token) throw new Error('Autenticação necessária');
            
            const response = await fetch(`${API_BASE_URL}/api/admin/categories`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(categoryData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Falha ao criar categoria');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao criar categoria:', error);
            throw error;
        }
    },
    
    updateCategory: async function(categoryId, categoryData) {
        try {
            const token = this.getToken();
            if (!token) throw new Error('Autenticação necessária');
            
            const response = await fetch(`${API_BASE_URL}/api/admin/categories/${categoryId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(categoryData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Falha ao atualizar categoria');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao atualizar categoria:', error);
            throw error;
        }
    },
    
    deleteCategory: async function(categoryId) {
        try {
            const token = this.getToken();
            if (!token) throw new Error('Autenticação necessária');
            
            const response = await fetch(`${API_BASE_URL}/api/admin/categories/${categoryId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Falha ao excluir categoria');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao excluir categoria:', error);
            throw error;
        }
    },
    
    createActivity: async function(activityData) {
        try {
            const token = this.getToken();
            if (!token) throw new Error('Autenticação necessária');
            
            const response = await fetch(`${API_BASE_URL}/api/admin/activities`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(activityData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Falha ao criar atividade');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao criar atividade:', error);
            throw error;
        }
    },
    
    // Busca de profissionais
    searchProfessionals: async function(filters = {}) {
        try {
            let url = `${API_BASE_URL}/api/search/professionals`;
            
            // Adicionar parâmetros de busca se fornecidos
            const params = new URLSearchParams();
            if (filters.activity) params.append('activity', filters.activity);
            if (filters.category) params.append('category', filters.category);
            if (filters.name) params.append('name', filters.name);
            
            if (params.toString()) {
                url += `?${params.toString()}`;
            }
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error('Falha ao buscar profissionais');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao buscar profissionais:', error);
            throw error;
        }
    },
    
    // Painel administrativo
    getPendingProfessionals: async function() {
        try {
            const token = this.getToken();
            if (!token) throw new Error('Autenticação necessária');
            
            const response = await fetch(`${API_BASE_URL}/api/admin/pending_professionals`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Falha ao buscar profissionais pendentes');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao buscar profissionais pendentes:', error);
            throw error;
        }
    },
    
    approveProfessional: async function(professionalId) {
        try {
            const token = this.getToken();
            if (!token) throw new Error('Autenticação necessária');
            
            const response = await fetch(`${API_BASE_URL}/api/admin/approve_professional/${professionalId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Falha ao aprovar profissional');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao aprovar profissional:', error);
            throw error;
        }
    },
    
    rejectProfessional: async function(professionalId) {
        try {
            const token = this.getToken();
            if (!token) throw new Error('Autenticação necessária');
            
            const response = await fetch(`${API_BASE_URL}/api/admin/reject_professional/${professionalId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Falha ao rejeitar profissional');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao rejeitar profissional:', error);
            throw error;
        }
    },
    
    // Visualização de diploma
    getDiploma: async function(professionalId) {
        try {
            const token = this.getToken();
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
            
            const response = await fetch(`${API_BASE_URL}/api/admin/diploma/${professionalId}`, {
                headers: headers
            });
            
            if (!response.ok) {
                throw new Error('Falha ao buscar diploma');
            }
            
            return await response.blob();
        } catch (error) {
            console.error('Erro ao buscar diploma:', error);
            throw error;
        }
    },
    
    // Detalhes do profissional
    getProfessionalDetails: async function(professionalId) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/search/professional/${professionalId}`);
            
            if (!response.ok) {
                throw new Error('Falha ao buscar detalhes do profissional');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao buscar detalhes do profissional:', error);
            throw error;
        }
    }
};
