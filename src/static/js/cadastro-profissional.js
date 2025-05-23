// Script para o cadastro de profissionais
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form');
    const registerButton = document.getElementById('register-button');
    const registerButtonText = document.getElementById('register-button-text');
    const registerSpinner = document.getElementById('register-spinner');
    const registerAlert = document.getElementById('register-alert');
    const registerSuccess = document.getElementById('register-success');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const categorySelect = document.getElementById('category');
    const activitiesContainer = document.getElementById('activities-container');
    const addActivityButton = document.getElementById('add-activity-button');

    // Verificar se o usuário já está autenticado
    if (window.api.isAuthenticated()) {
        window.location.href = 'index.html';
        return;
    }

    // Carregar categorias
    loadCategories();

    // Adicionar evento para adicionar nova atividade
    if (addActivityButton) {
        addActivityButton.addEventListener('click', addActivityField);
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
        
        // Verificar se o diploma foi selecionado
        const diplomaInput = document.getElementById('diploma');
        if (diplomaInput.files.length === 0) {
            diplomaInput.setCustomValidity('Por favor, selecione um arquivo de diploma');
            form.classList.add('was-validated');
            return;
        } else {
            diplomaInput.setCustomValidity('');
        }
        
        // Mostrar spinner e desabilitar botão
        registerButton.disabled = true;
        registerSpinner.classList.remove('d-none');
        registerButtonText.textContent = 'Cadastrando...';
        
        try {
            // Preparar dados para envio
            const formData = new FormData(form);
            
            // Garantir que document_number seja enviado
            if (formData.get('document') && !formData.get('document_number')) {
                formData.append('document_number', formData.get('document'));
            }
            
            // Enviar dados para a API
            const response = await window.api.registerProfessional(formData);
            
            // Mostrar mensagem de sucesso
            registerSuccess.classList.remove('d-none');
            form.reset();
            form.classList.remove('was-validated');
            
            // Limpar atividades adicionais
            const additionalActivities = document.querySelectorAll('.activity-row:not(:first-child)');
            additionalActivities.forEach(activity => activity.remove());
            
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
    
    // Carregar categorias da API
    async function loadCategories() {
        try {
            const categories = await window.api.getCategories();
            
            if (categories && categories.length > 0) {
                // Ordenar categorias por nome
                categories.sort((a, b) => a.name.localeCompare(b.name));
                
                // Adicionar opções ao select
                categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category.id;
                    option.textContent = category.name;
                    categorySelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Erro ao carregar categorias:', error);
        }
    }
    
    // Adicionar campo de atividade
    function addActivityField() {
        const activityCount = document.querySelectorAll('.activity-row').length;
        
        const activityRow = document.createElement('div');
        activityRow.className = 'activity-row row mb-3';
        
        activityRow.innerHTML = `
            <div class="col-md-6 mb-3">
                <label for="activity-${activityCount}" class="form-label">Nome da Atividade</label>
                <input type="text" class="form-control" id="activity-${activityCount}" name="activities[]" required>
                <div class="invalid-feedback">Por favor, informe o nome da atividade.</div>
            </div>
            <div class="col-md-6 mb-3">
                <label for="description-${activityCount}" class="form-label">Descrição</label>
                <input type="text" class="form-control" id="description-${activityCount}" name="descriptions[]" required>
                <div class="invalid-feedback">Por favor, informe uma descrição.</div>
            </div>
            <div class="col-md-6 mb-3">
                <label for="experience-${activityCount}" class="form-label">Anos de Experiência</label>
                <input type="number" class="form-control" id="experience-${activityCount}" name="experience_years[]" min="0" required>
                <div class="invalid-feedback">Por favor, informe os anos de experiência.</div>
            </div>
            <div class="col-md-6 mb-3">
                <label for="price-${activityCount}" class="form-label">Preço (R$)</label>
                <input type="number" class="form-control" id="price-${activityCount}" name="prices[]" min="0" step="0.01" required>
                <div class="invalid-feedback">Por favor, informe o preço.</div>
            </div>
            <div class="col-12 mb-3">
                <button type="button" class="btn btn-danger btn-sm remove-activity">Remover Atividade</button>
            </div>
        `;
        
        activitiesContainer.appendChild(activityRow);
        
        // Adicionar evento para remover atividade
        const removeButton = activityRow.querySelector('.remove-activity');
        removeButton.addEventListener('click', function() {
            activityRow.remove();
        });
    }
});
