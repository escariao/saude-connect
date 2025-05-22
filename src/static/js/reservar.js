// Script para a página de reserva de profissional
document.addEventListener('DOMContentLoaded', function() {
    // Variáveis globais
    let professionalData = null;
    let activities = [];
    let selectedActivity = null;
    let bookingId = null;
    
    // Verificar autenticação
    if (!window.api.isAuthenticated()) {
        alert('Você precisa estar logado como paciente para reservar um atendimento.');
        window.location.href = 'login.html';
        return;
    }
    
    // Verificar se é um paciente
    const userData = window.api.getUserData();
    if (userData.user_type !== 'patient') {
        alert('Apenas pacientes podem reservar atendimentos.');
        window.location.href = 'index.html';
        return;
    }
    
    // Obter ID do profissional da URL
    const urlParams = new URLSearchParams(window.location.search);
    const professionalId = urlParams.get('id');
    
    if (!professionalId) {
        alert('Profissional não especificado.');
        window.location.href = 'busca.html';
        return;
    }
    
    // Carregar dados do profissional
    loadProfessionalData(professionalId);
    
    // Configurar eventos
    document.getElementById('booking-form').addEventListener('submit', handleBookingSubmit);
    document.getElementById('payment-form').addEventListener('submit', handlePaymentSubmit);
    document.getElementById('payment-method').addEventListener('change', togglePaymentFields);
    
    // Configurar modal
    const modal = document.getElementById('payment-modal');
    const closeBtn = modal.querySelector('.close');
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    };
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };
    
    // Configurar seleção de atividade
    document.getElementById('activity').addEventListener('change', function() {
        const activityId = this.value;
        selectedActivity = activities.find(a => a.id == activityId);
        if (selectedActivity) {
            document.getElementById('activity-price-value').textContent = `R$ ${selectedActivity.price.toFixed(2)}`;
        } else {
            document.getElementById('activity-price-value').textContent = 'R$ 0,00';
        }
    });
    
    // Carregar dados do profissional
    async function loadProfessionalData(professionalId) {
        try {
            // Buscar dados do profissional
            const response = await fetch(`${window.api.baseUrl}/search/professional/${professionalId}`);
            
            if (!response.ok) {
                throw new Error('Erro ao buscar dados do profissional');
            }
            
            professionalData = await response.json();
            
            // Preencher dados do profissional
            document.getElementById('professional-name').textContent = professionalData.name;
            document.getElementById('professional-category').textContent = `Categoria: ${professionalData.category_name}`;
            document.getElementById('professional-id').value = professionalData.id;
            
            // Preencher avaliações
            if (professionalData.rating) {
                document.querySelector('.rating-value').textContent = professionalData.rating.toFixed(1);
                document.querySelector('.reviews-count').textContent = `(${professionalData.reviews_count || 0} avaliações)`;
                
                // Atualizar estrelas
                updateStars(professionalData.rating);
            }
            
            // Buscar atividades do profissional
            const activitiesResponse = await fetch(`${window.api.baseUrl}/search/professional/${professionalId}/activities`);
            
            if (!activitiesResponse.ok) {
                throw new Error('Erro ao buscar atividades do profissional');
            }
            
            activities = await activitiesResponse.json();
            
            // Preencher atividades
            const activitySelect = document.getElementById('activity');
            activitySelect.innerHTML = '<option value="">Selecione um serviço</option>';
            
            activities.forEach(activity => {
                const option = document.createElement('option');
                option.value = activity.id;
                option.textContent = `${activity.activity_name} - R$ ${activity.price.toFixed(2)}`;
                activitySelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Erro ao carregar dados do profissional:', error);
            alert('Erro ao carregar dados do profissional. Tente novamente mais tarde.');
        }
    }
    
    // Atualizar estrelas com base na avaliação
    function updateStars(rating) {
        const starsContainer = document.querySelector('.stars');
        starsContainer.innerHTML = '';
        
        // Adicionar estrelas cheias
        for (let i = 1; i <= Math.floor(rating); i++) {
            const star = document.createElement('i');
            star.className = 'fas fa-star';
            starsContainer.appendChild(star);
        }
        
        // Adicionar meia estrela se necessário
        if (rating % 1 >= 0.5) {
            const halfStar = document.createElement('i');
            halfStar.className = 'fas fa-star-half-alt';
            starsContainer.appendChild(halfStar);
        }
        
        // Adicionar estrelas vazias
        const emptyStars = 5 - Math.ceil(rating);
        for (let i = 0; i < emptyStars; i++) {
            const emptyStar = document.createElement('i');
            emptyStar.className = 'far fa-star';
            starsContainer.appendChild(emptyStar);
        }
    }
    
    // Manipular envio do formulário de reserva
    async function handleBookingSubmit(event) {
        event.preventDefault();
        
        // Validar formulário
        const form = event.target;
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        // Obter dados do formulário
        const formData = new FormData(form);
        const bookingData = {
            professional_id: formData.get('professional_id'),
            activity_id: formData.get('activity_id'),
            booking_date: formData.get('booking_date'),
            address: formData.get('address'),
            city: formData.get('city'),
            state: formData.get('state'),
            notes: formData.get('notes')
        };
        
        try {
            // Enviar dados para a API
            const response = await fetch(`${window.api.baseUrl}/booking/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(bookingData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erro ao criar reserva');
            }
            
            const result = await response.json();
            bookingId = result.booking_id;
            
            // Abrir modal de pagamento
            openPaymentModal();
            
        } catch (error) {
            console.error('Erro ao criar reserva:', error);
            alert(error.message || 'Erro ao criar reserva. Tente novamente mais tarde.');
        }
    }
    
    // Abrir modal de pagamento
    function openPaymentModal() {
        // Preencher dados no modal
        document.getElementById('modal-professional-name').textContent = professionalData.name;
        document.getElementById('modal-activity-name').textContent = selectedActivity.activity_name;
        document.getElementById('modal-booking-date').textContent = formatDate(document.getElementById('booking-date').value);
        document.getElementById('modal-price').textContent = `R$ ${selectedActivity.price.toFixed(2)}`;
        
        // Exibir modal
        document.getElementById('payment-modal').style.display = 'block';
    }
    
    // Formatar data
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    // Alternar campos de pagamento
    function togglePaymentFields() {
        const paymentMethod = document.getElementById('payment-method').value;
        const paymentFields = document.querySelectorAll('.payment-fields');
        
        // Esconder todos os campos
        paymentFields.forEach(field => {
            field.classList.add('hidden');
        });
        
        // Exibir campos específicos
        if (paymentMethod === 'credit_card' || paymentMethod === 'debit_card') {
            document.getElementById('credit-card-fields').classList.remove('hidden');
        } else if (paymentMethod === 'pix') {
            document.getElementById('pix-fields').classList.remove('hidden');
        } else if (paymentMethod === 'bank_transfer') {
            document.getElementById('bank-transfer-fields').classList.remove('hidden');
        }
    }
    
    // Manipular envio do formulário de pagamento
    async function handlePaymentSubmit(event) {
        event.preventDefault();
        
        // Validar formulário
        const form = event.target;
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        // Obter método de pagamento
        const paymentMethod = document.getElementById('payment-method').value;
        
        try {
            // Enviar dados para a API
            const response = await fetch(`${window.api.baseUrl}/booking/${bookingId}/payment`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ payment_method: paymentMethod })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erro ao processar pagamento');
            }
            
            // Fechar modal
            document.getElementById('payment-modal').style.display = 'none';
            
            // Exibir mensagem de sucesso
            alert('Reserva confirmada com sucesso! Você receberá um e-mail com os detalhes.');
            
            // Redirecionar para a página inicial
            window.location.href = 'index.html';
            
        } catch (error) {
            console.error('Erro ao processar pagamento:', error);
            alert(error.message || 'Erro ao processar pagamento. Tente novamente mais tarde.');
        }
    }
});
