const API_BASE_URL = "/api";

window.api = {
    getUserProfile: async function (userId) {
        try {
            const response = await fetch(`${API_BASE_URL}/user/${userId}`);
            if (!response.ok) throw new Error("Erro ao buscar perfil");
            return await response.json();
        } catch (error) {
            console.error("Erro em getUserProfile:", error);
            return null;
        }
    },

    searchProfessionals: async function (categoryId = null) {
        try {
            let url = `${API_BASE_URL}/search/professionals`;
            if (categoryId) {
                url += `?category_id=${categoryId}`;
            }
            const response = await fetch(url);
            if (!response.ok) throw new Error("Erro ao buscar profissionais");
            return await response.json();
        } catch (error) {
            console.error("Erro em searchProfessionals:", error);
            return [];
        }
    },

    registerPatient: async function (data) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register/patient`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error("Erro em registerPatient:", error);
            return { error: true };
        }
    },

    registerProfessional: async function (data) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register/professional`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error("Erro em registerProfessional:", error);
            return { error: true };
        }
    },

    updateProfile: async function (userId, data) {
        try {
            const response = await fetch(`${API_BASE_URL}/user/${userId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error("Erro em updateProfile:", error);
            return { error: true };
        }
    },

    getCategories: async function () {
        try {
            const response = await fetch(`${API_BASE_URL}/search/categories`);
            if (!response.ok) throw new Error("Erro ao buscar categorias");
            return await response.json();
        } catch (error) {
            console.error("Erro em getCategories:", error);
            return [];
        }
    }
};
