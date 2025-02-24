When cloning the repository on a new computer, follow these steps to set up the project:

---

### **1. Clone the Repository**

- Open a terminal and run:

  ```bash
  git clone <repository_url>
  ```

  Replace `<repository_url>` with the URL of your Git repository.

- Navigate into the cloned directory:
  ```bash
  cd chatbot
  ```

---

### **2. Set Up a Virtual Environment**

- Create and activate a virtual environment:
  ```bash
  python3 -m venv chatbot-env
  source chatbot-env/bin/activate
  ```
  For Windows:
  ```bash
  python -m venv chatbot-env
  chatbot-env\Scripts\activate
  ```

---

### **3. Install Dependencies**

- Install the Python libraries listed in `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

---

### **4. Set Up Environment Variables**

- Create a `.env` file in the project root if it doesn’t exist:
  ```bash
  touch .env
  ```
- Add your environment-specific variables, such as the OpenAI API key:
  ```
  OPENAI_API_KEY=ffff
  ```

---

### **5. Test the Application**

- Run the application locally to ensure it's working:
  ```bash
  uvicorn main:app --reload
  ```
- Open `http://127.0.0.1:8000` in your browser to view the FastAPI Swagger documentation.

---

### **6. Docker Setup**

If you're using Docker:
docker compose --env-file .env up -d
---
