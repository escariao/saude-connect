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
                throw new Error(data.message || data.error || 'Erro ao fazer login');
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
            const response = await fetch(`${this.baseUrl}/auth/register/patient`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(patientData)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || data.error || 'Erro ao cadastrar paciente');
            }
            
            return data;
        } catch (error) {
            console.error('Erro no cadastro de paciente:', error);
            throw error;
        }
    },
    
    // Método para cadastrar profissional
    registerProfessional: async function(formData) {
        try {
            // FormData já deve estar pronto para envio
            const response = await fetch(`${this.baseUrl}/auth/register/professional`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || data.error || 'Erro ao cadastrar profissional');
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
            // Retornar array vazio em caso de erro para evitar quebra da interface
            return [];
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
            // Retornar array vazio em caso de erro para evitar quebra da interface
            return [];
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
                throw new Error(data.message || data.error || 'Erro ao atualizar perfil');
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
                throw new Error(data.message || data.error || 'Erro ao atualizar perfil');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao atualizar perfil do profissional:', error);
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
            // Retornar array vazio em caso de erro para evitar quebra da interface
            return [];
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
                throw new Error(data.message || data.error || 'Erro ao aprovar profissional');
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
                throw new Error(data.message || data.error || 'Erro ao rejeitar profissional');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao rejeitar profissional:', error);
            throw error;
        }
    },
    
    // Método para criar uma reserva
    createBooking: async function(bookingData) {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Usuário não autenticado');
            }
            
            const response = await fetch(`${this.baseUrl}/booking/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(bookingData)
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || data.error || 'Erro ao criar reserva');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao criar reserva:', error);
            throw error;
        }
    },
    
    // Método para buscar reservas do usuário
    getUserBookings: async function(status = null) {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Usuário não autenticado');
            }
            
            let url = `${this.baseUrl}/booking/`;
            if (status) {
                url += `?status=${status}`;
            }
            
            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Erro ao buscar reservas');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao buscar reservas:', error);
            return [];
        }
    },
    
    // Método para processar pagamento de uma reserva
    processPayment: async function(bookingId, paymentMethod) {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Usuário não autenticado');
            }
            
            const response = await fetch(`${this.baseUrl}/booking/${bookingId}/payment`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ payment_method: paymentMethod })
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || data.error || 'Erro ao processar pagamento');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao processar pagamento:', error);
            throw error;
        }
    },
    
    // Método para atualizar status de uma reserva
    updateBookingStatus: async function(bookingId, status) {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Usuário não autenticado');
            }
            
            const response = await fetch(`${this.baseUrl}/booking/${bookingId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ status })
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || data.error || 'Erro ao atualizar status da reserva');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao atualizar status da reserva:', error);
            throw error;
        }
    },
    
    // Método para criar avaliação
    createReview: async function(bookingId, reviewData) {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('Usuário não autenticado');
            }
            
            const response = await fetch(`${this.baseUrl}/booking/${bookingId}/review`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(reviewData)
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || data.error || 'Erro ao criar avaliação');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao criar avaliação:', error);
            throw error;
        }
    },
    
    // Método para buscar avaliações de um profissional
    getProfessionalReviews: async function(professionalId) {
        try {
            const response = await fetch(`${this.baseUrl}/booking/professional/${professionalId}/reviews`);
            
            if (!response.ok) {
                throw new Error('Erro ao buscar avaliações');
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erro ao buscar avaliações:', error);
            return { reviews: [], count: 0, average_rating: 0 };
        }
    }
};
