
*Generate fully automated, SEO-optimized YouTube videos from a single topic prompt.*


## 🔧 Features

* ✅ Trending YouTube title generation from niche
* 🧠 AI-powered script writing (GROQAPI)
* 🎤 Voice-over generation (ElevenLabs TTS)
* 🎞️ Video creation with subtitles and visuals
* 🧠 SEO metadata optimization
* ⬆️ Auto-upload to YouTube with thumbnail support
* 🎯 Fully animated multi-step frontend interface

---

## 🧪 Tech Stack

* **Frontend**: HTML, TailwindCSS, JavaScript
* **Backend**: Python (Flask)
* **AI & APIs**: GroqAI, ElevenLabs, YouTube Data API
* **Media**: FFmpeg for video/audio handling
* **Extras**: Loguru for logging, .env for secure config

---

## 🚀 Setup Instructions

```bash
git clone https://github.com/yourname/youtube-auto-agent.git
cd youtube-auto-agent

# Setup virtual environment
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your API keys
cp .env.example .env

# Run the app
python main.py
```

Then open your browser at `http://127.0.0.1:5000/`

---



## 🖼️ UI Walkthrough

| Step                   | Description                                     |
| ---------------------- | ----------------------------------------------- |
| 🎯 Select Topic        | User enters a topic of interest                 |
| 🔥 Get Trending Titles | 5 YouTube titles are fetched via OpenAI         |
| 💡 Select Final Idea   | Choose one variation from suggested video ideas |
| 📝 Script Generation   | A full YouTube script is generated              |
| 🎤 Audio Generation    | Script is turned into voice using ElevenLabs    |
| 🎬 Video Generation    | Assets combined into a video with subtitles     |
| 📈 SEO Optimization    | Metadata and tags are generated                 |
| ⬆️ Upload to YouTube   | Video is uploaded with thumbnail                |

---

## 🗂️ Project Structure

```
youtube-auto-content-agent/
│
├── assets/
│   ├── audio/
│   ├── video/
│   └── thumbnails/
│
├── agents/
│   ├── idea_generator.py
│   ├── script_generator.py
│   ├── audio_generator.py
│   ├── video_generator.py
│   ├── seo_optimizer.py
│   └── uploader.py
│
├── static/
│   ├── style.css
│   └── script.js
│
├── template/
│   └── index.html
│
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── LICENSE
└── main.py
```


## 🛡 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙌 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you would like to change.

---

## 📬 Contact

Made by Bisma Riaz (https://github.com/bisma-codes) — feel free to reach out!
