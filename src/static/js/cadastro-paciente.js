// Script para o cadastro de paciente
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');
    const registerButton = document.getElementById('register-button');
    const registerSpinner = document.getElementById('register-spinner');
    const registerButtonText = document.getElementById('register-button-text');
    const registerAlert = document.getElementById('register-alert');
    const registerSuccess = document.getElementById('register-success');
    
    // Evitar validação automática no carregamento da página
    form.classList.remove('was-validated');
    
    // Função para validar o formulário
    function validateForm() {
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        
        // Verificar se as senhas conferem
        if (password !== confirmPassword) {
            document.getElementById('confirm-password').setCustomValidity('As senhas não conferem');
        } else {
            document.getElementById('confirm-password').setCustomValidity('');
        }
        
        // Verificar se o formulário é válido
        return form.checkValidity();
    }
    
    // Manipulador de envio do formulário
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        // Adicionar classe para ativar validação visual
        form.classList.add('was-validated');
        
        // Validar formulário
        if (!validateForm()) {
            return;
        }
        
        // Mostrar spinner e desabilitar botão
        registerButton.disabled = true;
        registerSpinner.classList.remove('d-none');
        registerButtonText.textContent = 'Cadastrando...';
        registerAlert.classList.add('d-none');
        
        try {
            // Preparar dados para envio
            const patientData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                password: document.getElementById('password').value,
                phone: document.getElementById('phone').value,
                document: document.getElementById('document-number').value, // Importante: usar 'document' como chave
                birth_date: document.getElementById('birth-date').value,
                address: document.getElementById('address').value,
                city: document.getElementById('city').value,
                state: document.getElementById('state').value
            };
            
            // Log para depuração
            console.log('Dados do paciente a serem enviados:', patientData);
            
            // Enviar dados para a API
            const response = await window.api.registerPatient(patientData);
            
            // Mostrar mensagem de sucesso
            registerSuccess.classList.remove('d-none');
            form.reset();
            form.classList.remove('was-validated');
            
            // Redirecionar para login após 2 segundos
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            
        } catch (error) {
            // Mostrar mensagem de erro
            registerAlert.textContent = error.message || 'Erro ao cadastrar paciente. Tente novamente.';
            registerAlert.classList.remove('d-none');
            
            // Rolar para o topo para mostrar a mensagem de erro
            window.scrollTo(0, 0);
        } finally {
            // Restaurar botão
            registerButton.disabled = false;
            registerSpinner.classList.add('d-none');
            registerButtonText.textContent = 'Cadastrar';
        }
    });
    
    // Validar confirmação de senha em tempo real
    document.getElementById('confirm-password').addEventListener('input', function() {
        const password = document.getElementById('password').value;
        const confirmPassword = this.value;
        
        if (password !== confirmPassword) {
            this.setCustomValidity('As senhas não conferem');
        } else {
            this.setCustomValidity('');
        }
    });
    
    // Validar senha em tempo real
    document.getElementById('password').addEventListener('input', function() {
        const confirmPassword = document.getElementById('confirm-password');
        if (confirmPassword.value) {
            if (this.value !== confirmPassword.value) {
                confirmPassword.setCustomValidity('As senhas não conferem');
            } else {
                confirmPassword.setCustomValidity('');
            }
        }
    });
});
