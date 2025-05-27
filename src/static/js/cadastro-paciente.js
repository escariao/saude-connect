// Script para o cadastro de pacientes
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');
    const registerButton = document.getElementById('register-button');
    const registerButtonText = document.getElementById('register-button-text');
    const registerSpinner = document.getElementById('register-spinner');
    const registerAlert = document.getElementById('register-alert');
    const registerSuccess = document.getElementById('register-success');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');

    // Verificar se o usuário já está autenticado
    if (window.api.isAuthenticated()) {
        window.location.href = 'index.html';
        return;
    }

    // Validar formulário no envio
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        // Limpar alertas anteriores
        registerAlert.classList.add('d-none');
        registerAlert.textContent = '';
        
        // Validar formulário
        if (!form.checkValidity()) {
            event.stopPropagation();
            form.classList.add('was-validated');
            return;
        }
        
        // Verificar se as senhas conferem
        if (passwordInput.value !== confirmPasswordInput.value) {
            confirmPasswordInput.setCustomValidity('As senhas não conferem');
            form.classList.add('was-validated');
            return;
        } else {
            confirmPasswordInput.setCustomValidity('');
        }
        
        // Mostrar spinner e desabilitar botão
        registerButton.disabled = true;
        registerSpinner.classList.remove('d-none');
        registerButtonText.textContent = 'Cadastrando...';
        
        try {
            // Preparar dados para envio
            const patientData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                password: passwordInput.value,
                document: document.getElementById('document-number').value, // Usar apenas document
                phone: document.getElementById('phone').value,
                birth_date: document.getElementById('birth-date').value,
                address: document.getElementById('address').value,
                city: document.getElementById('city').value,
                state: document.getElementById('state').value
            };
            
            // Enviar dados para a API
            const response = await window.api.registerPatient(patientData);
            
            // Mostrar mensagem de sucesso
            registerSuccess.classList.remove('d-none');
            form.reset();
            form.classList.remove('was-validated');
            
            // Redirecionar para a página de login após 2 segundos
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            
        } catch (error) {
            // Mostrar mensagem de erro
            registerAlert.textContent = error.message || 'Erro ao cadastrar. Tente novamente.';
            registerAlert.classList.remove('d-none');
            console.error('Erro no cadastro:', error);
        } finally {
            // Esconder spinner e habilitar botão
            registerButton.disabled = false;
            registerSpinner.classList.add('d-none');
            registerButtonText.textContent = 'Cadastrar';
        }
    });
    
    // Validar confirmação de senha em tempo real
    confirmPasswordInput.addEventListener('input', function() {
        if (passwordInput.value !== confirmPasswordInput.value) {
            confirmPasswordInput.setCustomValidity('As senhas não conferem');
        } else {
            confirmPasswordInput.setCustomValidity('');
        }
    });
    
    // Validar senha em tempo real
    passwordInput.addEventListener('input', function() {
        if (passwordInput.value !== confirmPasswordInput.value && confirmPasswordInput.value) {
            confirmPasswordInput.setCustomValidity('As senhas não conferem');
        } else {
            confirmPasswordInput.setCustomValidity('');
        }
    });
});
