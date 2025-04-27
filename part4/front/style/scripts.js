document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const email = loginForm.querySelector('input[type="email"]').value.trim();
            const password = loginForm.querySelector('input[type="password"]').value.trim();

            if (!email || !password) {
                alert("Veuillez remplir tous les champs.");
                return;
            }

            await loginUser(email, password);
        });
    }
});

// 👇 Fonction de connexion
async function loginUser(email, password) {
    try {
        const response = await fetch('http://localhost:5000/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include', // Nécessaire si ton backend utilise les cookies pour le token
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            const data = await response.json();

            // 🍪 Stockage du token dans un cookie
            const date = new Date();
            date.setTime(date.getTime() + (24 * 60 * 60 * 1000)); // 1 jour
            document.cookie = `token=${data.access_token}; expires=${date.toUTCString()}; path=/; SameSite=Lax`;

            // ✅ Redirection
            window.location.href = 'index.html';
        } else {
            const errorData = await response.json();
            alert('Échec de la connexion : ' + (errorData.message || 'Identifiants invalides'));
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Erreur de connexion au serveur');
    }
}
