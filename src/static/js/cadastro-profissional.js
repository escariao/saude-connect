// Script para o cadastro de profissional
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');
    const registerButton = document.getElementById('register-button');
    const registerSpinner = document.getElementById('register-spinner');
    const registerButtonText = document.getElementById('register-button-text');
    const registerAlert = document.getElementById('register-alert');
    const registerSuccess = document.getElementById('register-success');
    const addActivityBtn = document.getElementById('add-activity-btn');
    const activitiesContainer = document.getElementById('activities-container');
    
    // Evitar validação automática no carregamento da página
    form.classList.remove('was-validated');
    
    // Carregar categorias
    loadCategories();
    
    // Função para carregar categorias
    async function loadCategories() {
        try {
            const categories = await window.api.getCategories();
            const categorySelect = document.getElementById('category_id');
            
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                categorySelect.appendChild(option);
            });
        } catch (error) {
            console.error('Erro ao carregar categorias:', error);
        }
    }
    
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
        
        // Verificar se o diploma foi selecionado
        const diplomaFile = document.getElementById('diploma').files[0];
        if (!diplomaFile) {
            document.getElementById('diploma').setCustomValidity('Diploma é obrigatório');
        } else {
            document.getElementById('diploma').setCustomValidity('');
        }
        
        // Log para depuração
        console.log('Valor do documento:', document.getElementById('document').value);
        
        // Verificar se o formulário é válido
        return form.checkValidity();
    }
    
    // Adicionar nova atividade
    addActivityBtn.addEventListener('click', function() {
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item mb-3 p-3 border rounded';
        activityItem.innerHTML = `
            <div class="row">
                <div class="col-md-12 mb-2">
                    <label class="form-label">Nome da Atividade</label>
                    <input type="text" class="form-control activity-name" name="activities[]" required>
                    <div class="invalid-feedback">Por favor, informe o nome da atividade.</div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-2">
                    <label class="form-label">Anos de Experiência</label>
                    <input type="number" class="form-control activity-experience" name="experience_years[]" min="0" required>
                    <div class="invalid-feedback">Por favor, informe os anos de experiência.</div>
                </div>
                <div class="col-md-6 mb-2">
                    <label class="form-label">Preço (R$)</label>
                    <input type="number" class="form-control activity-price" name="prices[]" min="0" step="0.01" required>
                    <div class="invalid-feedback">Por favor, informe o preço.</div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-12">
                    <label class="form-label">Descrição</label>
                    <textarea class="form-control activity-description" name="descriptions[]" rows="2" required></textarea>
                    <div class="invalid-feedback">Por favor, descreva a atividade.</div>
                </div>
            </div>
            <button type="button" class="btn btn-outline-danger btn-sm mt-2 remove-activity-btn">
                <i class="bi bi-trash"></i> Remover Atividade
            </button>
        `;
        
        activitiesContainer.appendChild(activityItem);
        
        // Adicionar evento para remover atividade
        activityItem.querySelector('.remove-activity-btn').addEventListener('click', function() {
            activitiesContainer.removeChild(activityItem);
        });
    });
    
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
            const formData = new FormData(form);
            
            // Log para depuração
            console.log('FormData a ser enviado:');
            for (let [key, value] of formData.entries()) {
                console.log(key, value);
            }
            
            // Enviar dados para a API
            const response = await window.api.registerProfessional(formData);
            
            // Mostrar mensagem de sucesso
            registerSuccess.classList.remove('d-none');
            form.reset();
            form.classList.remove('was-validated');
            
            // Rolar para o topo para mostrar a mensagem de sucesso
            window.scrollTo(0, 0);
            
        } catch (error) {
            // Mostrar mensagem de erro
            registerAlert.textContent = error.message || 'Erro ao cadastrar profissional. Tente novamente.';
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
    
    // Limpar validação do diploma quando um arquivo for selecionado
    document.getElementById('diploma').addEventListener('change', function() {
        if (this.files.length > 0) {
            this.setCustomValidity('');
        }
    });
});
