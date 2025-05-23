// Script para o perfil do paciente
document.addEventListener('DOMContentLoaded', function() {
    // Verificar autenticação
    if (!window.api.isAuthenticated()) {
        document.getElementById('auth-alert').classList.remove('d-none');
        document.getElementById('profile-content').classList.add('d-none');
        return;
    }
    
    // Verificar se é paciente
    const userType = window.api.getUserType();
    if (userType !== 'patient') {
        document.getElementById('auth-alert').classList.remove('d-none');
        document.getElementById('auth-alert').innerHTML = 'Você não tem permissão para acessar esta página. <a href="index.html" class="alert-link">Voltar para a página inicial</a>.';
        document.getElementById('profile-content').classList.add('d-none');
        return;
    }
    
    // Mostrar conteúdo do perfil
    document.getElementById('auth-alert').classList.add('d-none');
    document.getElementById('profile-content').classList.remove('d-none');
    
    // Carregar perfil
    loadProfile();
    
    // Configurar logout
    document.getElementById('logout-link').addEventListener('click', function(e) {
        e.preventDefault();
        window.api.logout();
        window.location.href = 'index.html';
    });
    
    // Configurar formulário de edição
    document.getElementById('edit-profile-form').addEventListener('submit', function(e) {
        e.preventDefault();
        updateProfile();
    });
});

async function loadProfile() {
    const profileInfo = document.getElementById('profile-info');
    
    try {
        // Usar getUserProfile em vez de acessar diretamente getPatientProfile
        const profile = await window.api.getUserProfile();
        
        // Preencher informações do perfil
        let html = `
            <p><strong>Nome:</strong> ${profile.name}</p>
            <p><strong>Email:</strong> ${profile.email}</p>
            <p><strong>Telefone:</strong> ${profile.phone || 'Não informado'}</p>
            <p><strong>CPF:</strong> ${profile.document_number || 'Não informado'}</p>
        `;
        
        html += `
            <p><strong>Data de Nascimento:</strong> ${profile.birth_date ? formatDate(profile.birth_date) : 'Não informada'}</p>
            <p><strong>Endereço:</strong> ${profile.address || 'Não informado'}</p>
            <p><strong>Cidade/Estado:</strong> ${profile.city || 'Não informada'}${profile.state ? '/' + profile.state : ''}</p>
        `;
        
        profileInfo.innerHTML = html;
        
        // Preencher formulário de edição
        document.getElementById('edit-name').value = profile.name || '';
        document.getElementById('edit-phone').value = profile.phone || '';
        
        // Formatar data para o formato do input date
        if (profile.birth_date) {
            const date = new Date(profile.birth_date);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            document.getElementById('edit-birth-date').value = `${year}-${month}-${day}`;
        }
        
        document.getElementById('edit-address').value = profile.address || '';
        document.getElementById('edit-city').value = profile.city || '';
        document.getElementById('edit-state').value = profile.state || '';
        
    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
        profileInfo.innerHTML = `
            <div class="alert alert-danger">
                Erro ao carregar perfil: ${error.message || 'Tente novamente mais tarde.'}
            </div>
        `;
    }
}

async function updateProfile() {
    const name = document.getElementById('edit-name').value;
    const phone = document.getElementById('edit-phone').value;
    const birthDate = document.getElementById('edit-birth-date').value;
    const address = document.getElementById('edit-address').value;
    const city = document.getElementById('edit-city').value;
    const state = document.getElementById('edit-state').value;
    
    const alertContainer = document.getElementById('edit-alert');
    
    try {
        alertContainer.innerHTML = '<div class="alert alert-info">Atualizando perfil...</div>';
        
        const profileData = {
            name,
            phone,
            birth_date: birthDate,
            address,
            city,
            state
        };
        
        await window.api.updatePatientProfile(profileData);
        
        alertContainer.innerHTML = '<div class="alert alert-success">Perfil atualizado com sucesso!</div>';
        
        // Recarregar perfil
        loadProfile();
        
    } catch (error) {
        console.error('Erro ao atualizar perfil:', error);
        alertContainer.innerHTML = `<div class="alert alert-danger">${error.message || 'Erro ao atualizar perfil. Tente novamente.'}</div>`;
    }
}

// Função para formatar data
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}
