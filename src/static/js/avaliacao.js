// Script para avaliação de profissionais
document.addEventListener('DOMContentLoaded', function() {
    // Verificar autenticação
    if (!window.api.isAuthenticated()) {
        document.getElementById('review-section').classList.add('d-none');
        document.getElementById('login-required').classList.remove('d-none');
        return;
    }
    
    // Verificar se é um paciente
    const userData = window.api.getUserData();
    if (userData.user_type !== 'patient') {
        document.getElementById('review-section').classList.add('d-none');
        return;
    }
    
    // Elementos do DOM
    const reviewForm = document.getElementById('review-form');
    const ratingStars = document.querySelectorAll('.rating-input i');
    const ratingInput = document.getElementById('rating');
    const reviewsList = document.getElementById('reviews-list');
    const bookingSelect = document.getElementById('booking-select');
    
    // Obter ID do profissional da URL
    const urlParams = new URLSearchParams(window.location.search);
    const professionalId = urlParams.get('id');
    
    if (!professionalId) {
        console.error('ID do profissional não especificado');
        return;
    }
    
    // Carregar avaliações existentes
    loadReviews(professionalId);
    
    // Carregar reservas concluídas com este profissional
    loadCompletedBookings(professionalId);
    
    // Configurar eventos de estrelas
    ratingStars.forEach((star, index) => {
        star.addEventListener('click', () => {
            const rating = index + 1;
            ratingInput.value = rating;
            
            // Atualizar visual das estrelas
            ratingStars.forEach((s, i) => {
                if (i < rating) {
                    s.classList.remove('far');
                    s.classList.add('fas');
                } else {
                    s.classList.remove('fas');
                    s.classList.add('far');
                }
            });
        });
        
        // Efeito hover
        star.addEventListener('mouseenter', () => {
            const rating = index + 1;
            
            ratingStars.forEach((s, i) => {
                if (i < rating) {
                    s.classList.remove('far');
                    s.classList.add('fas');
                } else {
                    s.classList.remove('fas');
                    s.classList.add('far');
                }
            });
        });
    });
    
    // Restaurar estrelas ao sair do hover
    document.querySelector('.rating-input').addEventListener('mouseleave', () => {
        const rating = parseInt(ratingInput.value) || 0;
        
        ratingStars.forEach((s, i) => {
            if (i < rating) {
                s.classList.remove('far');
                s.classList.add('fas');
            } else {
                s.classList.remove('fas');
                s.classList.add('far');
            }
        });
    });
    
    // Enviar avaliação
    reviewForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const bookingId = bookingSelect.value;
        const rating = ratingInput.value;
        const comment = document.getElementById('comment').value;
        
        if (!bookingId) {
            alert('Por favor, selecione um atendimento para avaliar.');
            return;
        }
        
        if (!rating) {
            alert('Por favor, selecione uma avaliação de 1 a 5 estrelas.');
            return;
        }
        
        try {
            const response = await fetch(`${window.api.baseUrl}/booking/${bookingId}/review`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    rating: parseInt(rating),
                    comment: comment
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erro ao enviar avaliação');
            }
            
            // Limpar formulário
            reviewForm.reset();
            ratingInput.value = '';
            ratingStars.forEach(s => {
                s.classList.remove('fas');
                s.classList.add('far');
            });
            
            // Recarregar avaliações
            loadReviews(professionalId);
            
            // Recarregar reservas (para remover a que foi avaliada)
            loadCompletedBookings(professionalId);
            
            // Mostrar mensagem de sucesso
            alert('Avaliação enviada com sucesso!');
            
        } catch (error) {
            console.error('Erro ao enviar avaliação:', error);
            alert(error.message || 'Erro ao enviar avaliação. Tente novamente mais tarde.');
        }
    });
    
    // Carregar avaliações do profissional
    async function loadReviews(professionalId) {
        try {
            const response = await fetch(`${window.api.baseUrl}/booking/professional/${professionalId}/reviews`);
            
            if (!response.ok) {
                throw new Error('Erro ao carregar avaliações');
            }
            
            const data = await response.json();
            
            // Atualizar média de avaliações
            document.getElementById('average-rating').textContent = data.average_rating.toFixed(1);
            document.getElementById('reviews-count').textContent = `(${data.count} avaliações)`;
            
            // Atualizar lista de avaliações
            reviewsList.innerHTML = '';
            
            if (data.reviews.length === 0) {
                reviewsList.innerHTML = '<p>Nenhuma avaliação disponível.</p>';
                return;
            }
            
            data.reviews.forEach(review => {
                const reviewElement = document.createElement('div');
                reviewElement.className = 'review-item';
                
                const starsHtml = generateStarsHtml(review.rating);
                
                reviewElement.innerHTML = `
                    <div class="review-header">
                        <div class="review-user">${review.patient.name}</div>
                        <div class="review-date">${formatDate(review.created_at)}</div>
                    </div>
                    <div class="review-rating">${starsHtml}</div>
                    <div class="review-comment">${review.comment || ''}</div>
                `;
                
                reviewsList.appendChild(reviewElement);
            });
            
        } catch (error) {
            console.error('Erro ao carregar avaliações:', error);
            reviewsList.innerHTML = '<p>Erro ao carregar avaliações. Tente novamente mais tarde.</p>';
        }
    }
    
    // Carregar reservas concluídas
    async function loadCompletedBookings(professionalId) {
        try {
            const response = await fetch(`${window.api.baseUrl}/booking/?status=completed`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Erro ao carregar atendimentos concluídos');
            }
            
            const bookings = await response.json();
            
            // Filtrar reservas deste profissional que ainda não foram avaliadas
            const professionalBookings = bookings.filter(booking => 
                booking.professional.id == professionalId && !booking.reviewed
            );
            
            // Atualizar select de reservas
            bookingSelect.innerHTML = '<option value="">Selecione um atendimento concluído</option>';
            
            if (professionalBookings.length === 0) {
                bookingSelect.innerHTML += '<option value="" disabled>Nenhum atendimento disponível para avaliação</option>';
                document.getElementById('review-form-container').classList.add('d-none');
                document.getElementById('no-bookings-message').classList.remove('d-none');
                return;
            }
            
            professionalBookings.forEach(booking => {
                const option = document.createElement('option');
                option.value = booking.id;
                option.textContent = `Atendimento em ${formatDate(booking.booking_date)}`;
                bookingSelect.appendChild(option);
            });
            
            document.getElementById('review-form-container').classList.remove('d-none');
            document.getElementById('no-bookings-message').classList.add('d-none');
            
        } catch (error) {
            console.error('Erro ao carregar atendimentos:', error);
            bookingSelect.innerHTML = '<option value="">Erro ao carregar atendimentos</option>';
        }
    }
    
    // Gerar HTML das estrelas
    function generateStarsHtml(rating) {
        let html = '';
        
        // Estrelas cheias
        for (let i = 1; i <= Math.floor(rating); i++) {
            html += '<i class="fas fa-star"></i>';
        }
        
        // Meia estrela
        if (rating % 1 >= 0.5) {
            html += '<i class="fas fa-star-half-alt"></i>';
        }
        
        // Estrelas vazias
        const emptyStars = 5 - Math.ceil(rating);
        for (let i = 0; i < emptyStars; i++) {
            html += '<i class="far fa-star"></i>';
        }
        
        return html;
    }
    
    // Formatar data
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
});
