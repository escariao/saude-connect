// API client para o Saúde Connect
const API_BASE_URL = '';  // URL base vazia para usar o mesmo domínio

// Funções de autenticação
async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/user/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Erro ao fazer login');
        }
        
        // Salvar token no localStorage
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        return data;
    } catch (error) {
        console.error('Erro no login:', error);
        throw error;
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login.html';
}

function getAuthToken() {
    return localStorage.getItem('token');
}

function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function isAuthenticated() {
    return !!getAuthToken();
}

function getUserType() {
    const user = getCurrentUser();
    return user ? user.user_type : null;
}

// Funções para cadastro
async function registerPatient(patientData) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/patient/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(patientData),
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
}

async function registerProfessional(formData) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/register/professional`, {
            method: 'POST',
            body: formData,  // FormData para upload de arquivo
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
}

// Funções para busca de profissionais
async function searchProfessionals(activityId = null, category = null) {
    try {
        let url = `${API_BASE_URL}/api/search/professionals`;
        const params = new URLSearchParams();
        
        if (activityId) params.append('activity_id', activityId);
        if (category) params.append('category', category);
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }
        
        const response = await fetch(url);
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Erro ao buscar profissionais');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro na busca de profissionais:', error);
        throw error;
    }
}

async function getActivities() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/activities`);
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Erro ao buscar atividades');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro ao buscar atividades:', error);
        throw error;
    }
}

async function getActivityCategories() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/search/activities/categories`);
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Erro ao buscar categorias');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro ao buscar categorias:', error);
        throw error;
    }
}

// Funções para o painel administrativo
async function getPendingProfessionals() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/professionals/pending`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Erro ao buscar profissionais pendentes');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro ao buscar profissionais pendentes:', error);
        throw error;
    }
}

async function approveProfessional(profId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/professionals/${profId}/approve`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Erro ao aprovar profissional');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro ao aprovar profissional:', error);
        throw error;
    }
}

async function rejectProfessional(profId, reason) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/professionals/${profId}/reject`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getAuthToken()}`
            },
            body: JSON.stringify({ reason })
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Erro ao rejeitar profissional');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro ao rejeitar profissional:', error);
        throw error;
    }
}

// Funções para perfil do usuário
async function getUserProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/user/profile`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`
            }
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Erro ao buscar perfil');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro ao buscar perfil:', error);
        throw error;
    }
}

// Exportar todas as funções
window.api = {
    login,
    logout,
    getAuthToken,
    getCurrentUser,
    isAuthenticated,
    getUserType,
    registerPatient,
    registerProfessional,
    searchProfessionals,
    getActivities,
    getActivityCategories,
    getPendingProfessionals,
    approveProfessional,
    rejectProfessional,
    getUserProfile
};
