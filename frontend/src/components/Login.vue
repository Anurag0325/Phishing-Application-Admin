<template>
    <div>
        <nav class="navbar">
            <div class="navbar-brand">
                <img src="Xploit2Secure.jpeg" alt="Logo" class="logo" />
            </div>
        </nav>

        <div class="login-container">
            <h2>Login</h2>
            <form @submit.prevent="login">
                <div class="form-group">
                    <label for="Username">Username</label>
                    <input type="text" v-model="username" id="username" required />
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" v-model="password" id="password" required />
                </div>

                <button type="submit">Login</button>

                <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
            </form>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            username: '',
            password: '',
            errorMessage: null
        };
    },

    methods: {
        async login() {
            try {
                const response = await fetch('https://phishing-application-admin.onrender.com/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: this.username,
                        password: this.password
                    }),
                });

                const result = await response.json();
                if (response.ok) {
                    localStorage.setItem('access_token', result.access_token);
                    localStorage.setItem('username', this.username);
                    this.$router.push('/admin');  // Redirect to dashboard on success
                } else {
                    this.errorMessage = result.message || 'Login failed. Please try again.';
                }
            } catch (error) {
                this.errorMessage = "An error occurred during login. Please try again.";
                console.error(error);
            }
        }
    }
}
</script>

<style scoped>
.form-group {
    margin-bottom: 15px;
}

label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
    color: #333;
}

input {
    width: 100%;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #ddd;
    font-size: 14px;
    box-sizing: border-box;
    transition: border-color 0.3s ease;
}

input:focus {
    border-color: #26c8bb;
    outline: none;
    box-shadow: 0 0 5px rgba(38, 200, 187, 0.5);
}

/* Submit button */
button {
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg, #4df19f, #26c8bb);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    transition: background 0.3s ease, transform 0.3s ease;
}

button:hover {
    background: linear-gradient(135deg, #74cff3, #4df19f);
    transform: scale(1.05);
}

button:active {
    transform: scale(0.98);
}

/* Error message styling */
.error {
    color: red;
    text-align: center;
    margin-top: 15px;
    font-size: 14px;
}

/* Adding transition effects */
.error, .form-group, h2 {
    transition: transform 0.3s ease, opacity 0.3s ease;
}

</style>