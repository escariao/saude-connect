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
                if (response.status === 401) {
                    throw new Error('Email ou senha incorretos');
                } else if (response.status === 400) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || 'Dados de login inválidos');
                } else {
                    throw new Error('Erro no servidor. Tente novamente mais tarde.');
                }
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
        // Garantir que todos os dados de autenticação sejam removidos
        localStorage.removeItem('authState');
    },
    
    isAuthenticated: function() {
        try {
            const token = localStorage.getItem('token');
            const userData = localStorage.getItem('userData');
            
            // Verificação mais rigorosa para evitar falsos positivos
            if (!token || !userData) {
                this.logout(); // Garantir limpeza completa
                return false;
            }
            
            // Tentar analisar os dados do usuário para garantir que são válidos
            try {
                const user = JSON.parse(userData);
                if (!user || !user.id || !user.email || !user.user_type) {
                    this.logout(); // Limpar dados inválidos
                    return false;
                }
                
                // Verificar se o token não está vazio ou malformado
                if (token.length < 10) {
                    this.logout();
                    return false;
                }
                
                return true;
            } catch (e) {
                this.logout(); // Limpar dados corrompidos
                return false;
            }
        } catch (e) {
            // Em caso de erro (como acesso bloqueado ao localStorage), retornar false
            console.error('Erro ao verificar autenticação:', e);
            this.logout(); // Garantir limpeza
            return false;
        }
    },
    
    getUserData: function() {
        try {
            const userData = localStorage.getItem('userData');
            return userData ? JSON.parse(userData) : null;
        } catch (e) {
            this.logout(); // Limpar dados corrompidos
            return null;
        }
    },
    
    getUserType: function() {
        try {
            const userData = this.getUserData();
            return userData ? userData.user_type : null;
        } catch (e) {
            return null;
        }
    },
    
    getToken: function() {
        return localStorage.getItem('token');
    },
    
    // Perfil do usuário
    getUserProfile: async function() {
        try {
            const token = this.getToken();
            if (!token) throw new Error('Autenticação necessária');
            
            const userData = this.getUserData();
            if (!userData) throw new Error('Dados do usuário não encontrados');
            
            const userId = userData.id;
            const userType = userData.user_type;
            
            let endpoint = '';
            if (userType === 'patient') {
                endpoint = `/api/patient/${userId}`;
            } else if (userType === 'professional') {
                endpoint = `/api/professional/${userId}`;
            } else if (userType === 'admin') {
                return userData; // Admin não tem perfil adicional
            } else {
                throw new Error('Tipo de usuário desconhecido');
            }
            
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Perfil não encontrado');
                } else {
                    throw new Error('Erro ao carregar perfil');
                }
            }
            
            const profileData = await response.json();
            return {
                ...userData,
                ...profileData
            };
        } catch (error) {
            console.error('Erro ao buscar perfil do usuário:', error);
            throw error;
        }
    },
    
    updateUserProfile: async function(profileData) {
        try {
            const token = this.getToken();
            if (!token) throw new Error('Autenticação necessária');
            
            const userData = this.getUserData();
            if (!userData) throw new Error('Dados do usuário não encontrados');
            
            const userId = userData.id;
            const userType = userData.user_type;
            
            let endpoint = '';
            if (userType === 'patient') {
                endpoint = `/api/patient/${userId}`;
            } else if (userType === 'professional') {
                endpoint = `/api/professional/${userId}`;
            } else {
                throw new Error('Atualização de perfil não disponível para este tipo de usuário');
            }
            
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(profileData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Falha ao atualizar perfil');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao atualizar perfil:', error);
            throw error;
        }
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
                if (response.status === 400) {
                    const errorData = await response.json();
                    if (errorData.error && errorData.error.includes('Email já cadastrado')) {
                        throw new Error('Este email já está em uso. Por favor, utilize outro email ou faça login.');
                    } else {
                        throw new Error(errorData.error || 'Dados de cadastro inválidos');
                    }
                } else {
                    throw new Error('Erro no servidor. Tente novamente mais tarde.');
                }
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro no cadastro de paciente:', error);
            throw error;
        }
    },
    
    registerProfessional: async function(formData) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/register/professional`, {
                method: 'POST',
                body: formData // FormData já está configurado para multipart/form-data
            });
            
            if (!response.ok) {
                if (response.status === 400) {
                    const errorData = await response.json();
                    if (errorData.error && errorData.error.includes('Email já cadastrado')) {
                        throw new Error('Este email já está em uso. Por favor, utilize outro email ou faça login.');
                    } else {
                        throw new Error(errorData.error || 'Dados de cadastro inválidos');
                    }
                } else {
                    throw new Error('Erro no servidor. Tente novamente mais tarde.');
                }
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
            const response = await fetch(`${API_BASE_URL}/api/search/categories`);
            
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
            if (filters.activity) params.append('activity_id', filters.activity);
            if (filters.category) params.append('category', filters.category);
            if (filters.name) params.append('name', filters.name);
            
            if (params.toString()) {
                url += `?${params.toString()}`;
            }
            
            const response = await fetch(url);
            
            if (!response.ok) {
                if (response.status === 404) {
                    return []; // Retornar array vazio se não encontrar profissionais
                } else {
                    throw new Error('Falha ao buscar profissionais');
                }
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
                if (response.status === 404) {
                    return []; // Retornar array vazio se não encontrar profissionais pendentes
                } else {
                    throw new Error('Falha ao buscar profissionais pendentes');
                }
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
                if (response.status === 404) {
                    throw new Error('Profissional não encontrado');
                } else {
                    throw new Error('Falha ao buscar detalhes do profissional');
                }
            }
            
            return await response.json();
        } catch (error) {
            console.error('Erro ao buscar detalhes do profissional:', error);
            throw error;
        }
    }
};
