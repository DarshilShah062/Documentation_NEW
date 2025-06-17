Great! Here's a **complete step-by-step guide** to deploy your Streamlit app that uses:

* 📂 **Google Drive** (for storage),
* 📡 **Pinecone** (vector DB),
* 🧠 **OpenAI API** (LLM),
* 🚀 **Deployment on [Streamlit Cloud](https://streamlit.io/cloud)** with **secrets management**.

---

## ✅ Step-by-Step Deployment Plan

### **1. Project Structure**

```
your-project/
│
├── app.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
```

---

### **2. Code: `app.py` (Sample Template)**

```python
import streamlit as st
import pinecone
import openai
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- SETUP API KEYS ---
openai.api_key = st.secrets["openai_api_key"]
pinecone.init(api_key=st.secrets["pinecone_api_key"], environment=st.secrets["pinecone_env"])

# --- GOOGLE DRIVE SETUP ---
gdrive_creds = service_account.Credentials.from_service_account_info(st.secrets["gdrive_creds"])
drive_service = build('drive', 'v3', credentials=gdrive_creds)

# --- PINECONE INDEX ---
index = pinecone.Index("your-index-name")

# --- UI ---
st.title("📚 Chat with your Google Drive Document")

query = st.text_input("Ask a question:")
if query:
    # Dummy logic: fetch top match from Pinecone, send to OpenAI
    results = index.query(vector=[0.1]*1536, top_k=1, include_metadata=True)  # placeholder
    context = results['matches'][0]['metadata']['text'] if results['matches'] else "No match found."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Answer based on context."},
            {"role": "user", "content": f"Context: {context}\n\nQ: {query}"}
        ]
    )
    st.write(response['choices'][0]['message']['content'])
```

---

### **3. `requirements.txt`**

```txt
streamlit
openai
pinecone-client
google-api-python-client
google-auth
```

---

### **4. Create `.streamlit/config.toml`**

```toml
[theme]
base="light"
```

---

### **5. Push to GitHub**

1. Create a GitHub repo
2. Push your project:

```bash
git init
git remote add origin https://github.com/your-username/your-repo.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

---

### **6. Deploy on [Streamlit Cloud](https://streamlit.io/cloud)**

* Sign in and click **“New App”**
* Choose your GitHub repo and branch
* Click **“Deploy”**

---

### **7. Add Secrets via Streamlit Cloud**

Go to the **Secrets Manager** tab and add:

```toml
openai_api_key = "sk-..."

pinecone_api_key = "your-pinecone-key"
pinecone_env = "us-west1-gcp"

[gdrive_creds]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "xyz@project.iam.gserviceaccount.com"
client_id = "..."
```

---

### ✅ Done! Your app will now be live at:

```
https://<your-repo-name>.streamlit.app
```

---

Would you like me to:

* Create a GitHub template repo for you?
* Generate a working example from scratch with Google Drive + Pinecone + OpenAI?

Let me know!
