<template>
    <div v-if="showPopup" class="popup">
        <div class="popup-content">
            <!-- Phishing alert content -->

            <div v-if="!showStudyMaterial && !showQuestions && !showCloseButton" class="alert-popup">
                <h2 class="popup-title">Alert: Phishing Attempt Detected!</h2>
                <p class="warning-text blinking">
                    You've clicked on a link from a suspicious email, which could have led to a phishing attack. Cybercriminals use such tricks to steal sensitive information like your passwords, financial details, or personal data.
                </p>
                <p class="warning-text blinking">
                    To stay safe online, always verify the source of emails before clicking on any links. Don't worry, you're not in trouble—this is a simulated phishing test to help you learn!
                </p>
                <p class="warning-text blinking">
                    Please attend the tutorial to enhance your awareness and protect yourself from future threats.
                </p>
                <button class="button-primary" @click="startTutorial">Attend Tutorial</button>
            </div>


            <!-- Study Material Section -->
            <div v-if="showStudyMaterial && !showQuestions" ref="studyMaterialSection">
                <h2 class="popup-title">Study Material</h2>

                <div class="content-section">
                    <h3 class="section-title">Course Content</h3>
                    <ul class="content-list">
                        <li class="content-item">1. What is Phishing?</li>
                        <li class="content-item">2. Common Phishing Techniques</li>
                        <li class="content-item">3. How to Recognize Phishing Emails</li>
                        <li class="content-item">4. Best Practices for Online Safety</li>
                    </ul>
                </div>

                <!-- Video Section (Google Slide presentation) -->
                <div class="video-section">
                    <h3 class="video-title">Phishing Awareness Tutorial</h3>
                    <iframe
                        ref="presentationIframe" 
                        src="https://docs.google.com/presentation/d/e/2PACX-1vSkHqHBoKf3xM2yy9QMU-98GbyywQACmHqLX2Uno-xI1zDcIWckVC8_PjYqO34UW2RGMbFqZgnCc170/embed?start=true&loop=false&delayms=3000" 
                        frameborder="0"
                        class="presentation-iframe" 
                        allowfullscreen
                        mozallowfullscreen 
                        webkitallowfullscreen>
                    </iframe>
                </div>

                <button 
                    class="button-primary" 
                    :disabled="!isPresentationCompleted"  
                    @click="fetchQuestions">
                    Start Quiz
                </button>
            </div>

            <!-- Quiz Section -->
            <div v-if="showQuestions" class="questions-container">
                <h2 class="popup-title">Quiz: Phishing Awareness</h2>
                <div class="questions-wrapper">
                    <div v-for="(question, index) in questions" :key="index" class="question">
                        <p class="question-text">{{ question.question_text }}</p>
                        <ul class="options-list">
                            <li v-for="(option, idx) in question.options" :key="idx" class="option-item">
                                <label class="option-label">
                                    <input type="radio" :name="'question_' + index" :value="option" v-model="answers[index]" />
                                    {{ option }}
                                </label>
                            </li>
                        </ul>
                    </div>
                </div>
                <button class="button-primary" @click="submitAnswers">Submit Answers</button>
            </div>

            <div v-if="showCloseButton">
                <p>Thank you for participating in the data phishing awareness program. Soon you will get your result.</p>
                <button class="button-secondary" @click="closePopup">Close</button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            showPopup: false,
            showStudyMaterial: false,
            showQuestions: false,
            showCloseButton: false,
            questions: [],
            answers: [],
            isPresentationCompleted: false,
        };
    },
    created() {
        const colleagueId = this.$route.params.colleague_id;
        this.fetchData(colleagueId);
    },
    methods: {
        // async fetchData(colleagueId) {
        //     try {
        //         const response = await fetch(`http://127.0.0.1:5000/phishing_opened/${colleagueId}`);
        //         const data = await response.json();
        //         if (data.showPopup) {
        //             this.showPopup = true;
        //         } else {
        //             this.showPopup = false;
        //         }
        //     } catch (error) {
        //         console.error('Error fetching data:', error);
        //     }
        // },


        async fetchData(colleagueId) {
    console.log('Fetching data for colleague ID:', colleagueId); // Check what ID is being sent
    try {
        const response = await fetch(`https://phishing-application-admin.onrender.com/phishing_opened/${colleagueId}`);
        const data = await response.json();
        console.log('Response data:', data); // Log the response data
        if (data.showPopup) {
            this.showPopup = true;
        } else {
            this.showPopup = false;
        }
    } catch (error) {
        console.error('Error fetching data:', error);
    }
},

        startTutorial() {
            this.showStudyMaterial = true;
            this.$nextTick(() => {
                this.enterFullScreen();
                this.trackPresentationCompletion();
            });
        },
        enterFullScreen() {
            const studyMaterialSection = this.$refs.studyMaterialSection;

            if (studyMaterialSection && studyMaterialSection.requestFullscreen) {
                studyMaterialSection.requestFullscreen();
            } else if (studyMaterialSection && studyMaterialSection.mozRequestFullScreen) {
                studyMaterialSection.mozRequestFullScreen();
            } else if (studyMaterialSection && studyMaterialSection.webkitRequestFullscreen) {
                studyMaterialSection.webkitRequestFullscreen();
            } else if (studyMaterialSection && studyMaterialSection.msRequestFullscreen) {
                studyMaterialSection.msRequestFullscreen();
            } else {
                console.warn("Full screen is not supported");
            }
            document.addEventListener('keydown', this.preventEsc);
        },
        preventEsc(event) {
            if (event.key === "Escape") {
                event.preventDefault();
            }
        },
        trackPresentationCompletion() {
            const presentationDuration = 30000;
            setTimeout(() => {
                this.isPresentationCompleted = true;
            }, presentationDuration);
        },
        async fetchQuestions() {
            try {
                const response = await fetch(`https://phishing-application-admin.onrender.com/questions`);
                const data = await response.json();
                this.questions = data;
                this.answers = Array(data.length).fill(null);
                this.showQuestions = true;
            } catch (error) {
                console.error('Error fetching questions:', error);
            }
        },
        async submitAnswers() {
            const colleagueId = this.$route.params.colleague_id;
            try {
                const response = await fetch(`https://phishing-application-admin.onrender.com/submit_answers/${colleagueId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ answers: this.answers }),
                });
                const result = await response.json();
                if (result.message) {
                    this.showQuestions = false;
                    this.showStudyMaterial = false;
                    this.showCloseButton = true;
                }
            } catch (error) {
                console.error('Error submitting answers:', error);
            }
        },
        closePopup() {
            this.showPopup = false;
            window.close();
        }
    }
};
</script>

<style scoped>


.warning-text {
    font-size: 0.9em; 
    color: #333;
    margin: 10px 0;
    line-height: 1.5;
}

.study-material-container {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.video-section {
    width: 100%;
    margin-bottom: 20px;
}

.content-section {
    text-align: left;
    margin-bottom: 20px;
}

.presentation-iframe {
    width: 100%;
    height: 400px;
    border: none;
}

.section-title {
    font-size: 1.3em; 
    margin-bottom: 10px;
}

.content-list {
    list-style: none;
    padding: 0;
}

.content-item {
    font-size: 0.9em;
    margin: 5px 0;
}

.popup {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
}

.popup-content {
    background: #ffffff;
    border-radius: 16px;
    width: 100%;
    max-width: 800px;
    max-height: 90vh;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    padding: 20px;
    text-align: center;
    overflow-y: auto;
    animation: fadeIn 0.3s ease-in-out;
}

.popup-title {
    font-size: 1.8em;
    color: #007bff;
    margin-bottom: 20px;
    font-weight: 700;
}

.questions-container {
    margin-top: 20px;
}

.questions-wrapper {
    text-align: left;
}

.question {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.question-text {
    font-size: 1.2em;
    margin-bottom: 10px;
    font-weight: 600;
}

.options-list {
    list-style: none;
    padding: 0;
}

.option-item {
    margin: 5px 0;
}

.option-label {
    display: flex;
    align-items: center;
    padding: 10px;
    background: #e9ecef;
    border-radius: 5px;
    cursor: pointer;
    transition: background 0.2s;
}

.option-label:hover {
    background: #d6d8db;
}

.button-primary, .button-secondary {
    padding: 10px 15px;
    font-size: 1.1em;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 20px;
}

.button-primary {
    background-color: #007bff;
    color: white;
    transition: background 0.2s;
}

.button-primary:hover {
    background-color: #0056b3;
}

.button-secondary {
    background-color: #6c757d;
    color: white;
}

.button-secondary:hover {
    background-color: #5a6268;
}

.button-primary {
    padding: 10px 15px;
    font-size: 1.1em;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 20px;
    background-color: #007bff;
    color: white;
    transition: background 0.2s;
}

.button-primary:disabled {
    background-color: #ccc;
    color: #666;
    cursor: not-allowed;
}

.button-primary:not(:disabled):hover {
    background-color: #0056b3;
}

.alert-popup {
    background-color: #fff3cd;
    border: 1px solid #ffeeba;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    max-width: 600px;
    margin: 20px auto;
    text-align: center;
}

.warning-text {
    color: #856404;
    font-size: 16px;
    line-height: 1.5;
    margin-bottom: 10px;
}

.blinking {
    animation: blink-animation 1s steps(5, start) infinite;
}

@keyframes blink-animation {
    to {
        visibility: hidden;
    }
}
</style>

